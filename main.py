from states import welcome, Ready, run_question
from score import calculate_total_score
# from receipt import generate_receipt
from face import close_face_camera

NUM_QUESTIONS = 3
ANSWER_DURATION = 10


def main():
    question_results = []

    # ----------------------------
    # WELCOME STATE
    # ----------------------------
    welcome()

    is_ready = Ready()

    if not is_ready:
        print("User is not ready. Ending experience.")
        return Ready()  # Optionally, you could loop back to welcome or exit the program here.

    # ----------------------------
    # QUESTION STATES
    # ----------------------------
    for question_number in range(1, NUM_QUESTIONS + 1):
        result = run_question(
            question_number=question_number,
            answer_duration=ANSWER_DURATION
        )

        question_results.append(result)

    # ----------------------------
    # FINAL SCORE
    # ----------------------------
    total_result = calculate_total_score(question_results)

    print("")
    print("========== FINAL RESULT ==========")
    print(total_result)

    # ----------------------------
    # RECEIPT
    # ----------------------------
    receipt_data = {
        "score": total_result["final_score"],
        "face": total_result["face_score"],
        "voice": total_result["voice_score"],
        "text": total_result["text_score"],
        "label": total_result["label"],
        "authenticity": total_result["authenticity"],

        # optional receipt values
        "valence": round(
            sum(q.get("valence", 0) for q in question_results) / len(question_results),
            2
        ),
        "thinking": round(
            sum(q.get("thinking", 0) for q in question_results) / len(question_results),
            2
        ),
        "arousal": round(
            sum(q.get("arousal", 0) for q in question_results) / len(question_results),
            2
        ),
        "anxious": round(
            sum(q.get("anxious", 0) for q in question_results) / len(question_results),
            2
        ),
    }

    # img = generate_receipt(receipt_data)
    # img.save("final_receipt.png")
    # img.show()

    # Later:
    # print_receipt("final_receipt.png")

    close_face_camera()


if __name__ == "__main__":
    main()