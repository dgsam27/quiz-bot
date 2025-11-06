
from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST


def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if current_question_id is None:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id)

    if next_question:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    try:
        if current_question_id is None:
            return True, ""
        answer = answer.strip()
        if answer in PYTHON_QUESTION_LIST[current_question_id]['options']:

            if current_question_id == 0 or "question_ans" not in session:
                session["question_ans"] = [{"question_id":current_question_id, "user_ans":answer}]
            else:
                session["question_ans"].append({"question_id":current_question_id, "user_ans":answer})
            session.save()
            return True, ""
        else:
            return False, "Invalid answer. Please enter the answers from the shown options"
    except Exception as e:
        print("Exception in record current ans: ", str(e))
        return False, "Unexpected Error: Try after some time..."


def get_next_question(current_question_id):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    try:
        if current_question_id is None:
            next_question_id = 0
            question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
            options = PYTHON_QUESTION_LIST[next_question_id]["options"]

            formatted_options = "\n".join([f"• {opt}" for opt in options])
            formatted_text = f"{question}\n{formatted_options}"
            return formatted_text, next_question_id
        elif current_question_id >= len(PYTHON_QUESTION_LIST)-1: #If the question is invalid/out of the questions list
            return "", -1
        else:
            next_question_id = current_question_id+1
            question = PYTHON_QUESTION_LIST[next_question_id]["question_text"]
            options = PYTHON_QUESTION_LIST[next_question_id]["options"]

            formatted_options = "\n".join([f"• {opt}" for opt in options])
            formatted_text = f"{question}\n{formatted_options}"
            return formatted_text, next_question_id if current_question_id <= len(PYTHON_QUESTION_LIST) - 1 else -1
    except Exception as e:
        print("Exception in get next question:", str(e))
        return "Unexpected Error: Try after some time...", -1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    total_score = 0
    for qst_ans_dict in session["question_ans"]:
        if qst_ans_dict["user_ans"] == PYTHON_QUESTION_LIST[qst_ans_dict["question_id"]]["answer"]:
            total_score+=1
    score_percentage = (total_score/len(PYTHON_QUESTION_LIST))*100
    if score_percentage <= 40:
        final_score_msg = f"Good effort! You have made a start and scored {total_score}/{len(PYTHON_QUESTION_LIST)}. Keep practicing — every step counts toward improvement!"
    elif score_percentage > 40 and score_percentage <= 75:
        final_score_msg = f"Nice work! You scored {total_score}/{len(PYTHON_QUESTION_LIST)}. You’re halfway there — with a bit more focus, you’ll nail it next time!"
    elif score_percentage > 75 and score_percentage <= 90:
        final_score_msg = f"Great job! You scored {total_score}/{len(PYTHON_QUESTION_LIST)}. You are almost at the top — just a little more effort and you’ll master it!"
    else:
        final_score_msg = f"Outstanding! You scored {total_score}/{len(PYTHON_QUESTION_LIST)} Perfect score — your hard work really shows. Keep up the amazing performance!"
    return final_score_msg
