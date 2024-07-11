from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    # Check if the initial message is a greeting
    if message.lower() == "hi":
        bot_responses.append(BOT_WELCOME_MESSAGE)
        question, options, current_question_id = get_next_question(None)
        session["current_question_id"] = current_question_id
        session["correct_answers_count"] = 0
        session["questions_asked_count"] = 0
        bot_responses.append(f"Question:\n\n{question}\n\nOption List:\n{options}")
    else:
        current_question_id = session.get("current_question_id")
        correct_answers_count = session.get("correct_answers_count", 0)
        questions_asked_count = session.get("questions_asked_count", 0)

        if current_question_id is None or current_question_id < 0:
            bot_responses.append(BOT_WELCOME_MESSAGE)
            question, options, current_question_id = get_next_question(None)
            session["current_question_id"] = current_question_id
            session["correct_answers_count"] = 0
            session["questions_asked_count"] = 0
            bot_responses.append(f"Question:\n\n{question}\n\nOption List:\n{options}")
        else:
            if message.lower() == "exit":
                final_response = generate_final_response(session)
                bot_responses.append(final_response)
            else:
                success, error, correct_answer = record_current_answer(message, current_question_id, session)
                if success:
                    correct_answers_count += 1
                    session["correct_answers_count"] = correct_answers_count
                    bot_responses.append("Correct Answer!")
                else:
                    bot_responses.append(error)
                    bot_responses.append(f"The correct answer is: {correct_answer}")

                question, options, next_question_id = get_next_question(current_question_id)
                if question:
                    questions_asked_count += 1
                    session["questions_asked_count"] = questions_asked_count
                    session["current_question_id"] = next_question_id
                    bot_responses.append(f"Question:\n{question}\nOption List:\n{options}")
                else:
                    final_response = generate_final_response(session)
                    bot_responses.append(final_response)

    session.save()

    return bot_responses

def record_current_answer(answer, current_question_id, session):
    current_question = PYTHON_QUESTION_LIST[current_question_id]
    correct_answer = current_question["answer"]
    if answer.lower() == correct_answer.lower():
        answers = session.get("answers", [])
        answers.append({"question_id": current_question_id, "answer": answer})
        session["answers"] = answers
        return True, "", correct_answer
    else:
        return False, f"Incorrect answer.", correct_answer

def get_next_question(current_question_id):
    if current_question_id is None:
        return PYTHON_QUESTION_LIST[0]["question_text"], PYTHON_QUESTION_LIST[0]["options"], 0
    elif current_question_id < len(PYTHON_QUESTION_LIST) - 1:
        return PYTHON_QUESTION_LIST[current_question_id + 1]["question_text"], PYTHON_QUESTION_LIST[current_question_id + 1]["options"], current_question_id + 1
    else:
        return None, [], -1

def generate_final_response(session):
    correct_answers_count = session.get("correct_answers_count", 0)
    questions_asked_count = session.get("questions_asked_count", 0)
    score = (correct_answers_count / questions_asked_count) * 100
    return f"Your final score is: {score:.2f}%. You answered {correct_answers_count} out of {questions_asked_count} questions correctly."
