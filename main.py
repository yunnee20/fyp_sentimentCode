from xmlrpc import client

from states import welcome, Ready, run_question
from score import calculate_total_score
# from receipt import generate_receipt
from face import close_face_camera
from receipt import save_and_print_receipt
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 8001)

NUM_QUESTIONS = 3
ANSWER_DURATION = 10


def main():
    
    client.send_message("/state", 0)
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
    avg_valence = sum(q["valence"] for q in question_results) / len(question_results)
    avg_thinking = sum(q["thinking"] for q in question_results) / len(question_results)
    avg_arousal = sum(q["arousal"] for q in question_results) / len(question_results)
    avg_anxious = sum(q["anxious"] for q in question_results) / len(question_results)

    receipt_data = {
        "score": total_result["final_score"],
        "face": total_result["face_score"],
        "voice": total_result["voice_score"],
        "text": total_result["text_score"],
        "label": total_result["label"],
        "authenticity": total_result["authenticity"],

        "valence": round(avg_valence, 2),
        "thinking": round(avg_thinking, 2),
        "arousal": round(avg_arousal, 2),
        "anxious": round(avg_anxious, 2),
    }

    # save_and_print_receipt(receipt_data)

    close_face_camera()


if __name__ == "__main__":
    main()