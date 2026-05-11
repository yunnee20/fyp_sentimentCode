from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 8001)

from face import start_face_stream, stop_face_stream, get_average_face_values
from textsentiment import analyze_text_sentiment
from score import calculate_final_score
from voicetotext import voice_to_text, check_ready
from voice_freqpitch import start_voice_stream, stop_voice_stream, get_voice_score


ready = False
startTest = False

def welcome():
    client.send_message("/state", 0)
    global ready

    print("Now playing welcome video and music.")
    ready = True


def Ready():
    global startTest

    print("Say ready after the beep...")

    text = voice_to_text(duration=5)

    if check_ready():
        startTest = True
        return True

    return False


def run_question(question_number, answer_duration=10):
    print("")
    print(f"---------- QUESTION {question_number} START ----------")
    client.send_message("/state", question_number)
    # Start real-time streams to TouchDesigner
    start_face_stream(camera_index=1, show=True)
    start_voice_stream()

    # Record and transcribe answer while streams are running
    transcript = voice_to_text(duration=answer_duration)

    # Stop real-time streams when answer ends
    stop_face_stream()
    stop_voice_stream()

    # Get average scores collected during the answer
    face_values = get_average_face_values()
    face_score = face_values["face_score"]
    voice_score = get_voice_score()

    # Analyze transcript
    text_result = analyze_text_sentiment(transcript)
    text_score = text_result["suboptimal_score"]

    # Combine scores
    question_score = calculate_final_score(
        face_score=face_score,
        voice_score=voice_score,
        text_score=text_score
    )

    question_result = {
        "question_number": question_number,
        "transcript": transcript,

        "valence": round(face_values["valence"], 2),
        "thinking": round(face_values["thinking"], 2),
        "arousal": round(face_values["arousal"], 2),
        "anxious": round(face_values["anxious"], 2),

        "face_score": round(face_score, 2),
        "voice_score": round(voice_score, 2),
        "text_score": round(text_score, 2),

        **text_result,
        **question_score
    }

    print("")
    print("---------- QUESTION RESULT ----------")
    print("Transcript:", transcript)
    print("Face Score:", round(face_score, 2))
    print("Voice Score:", round(voice_score, 2))
    print("Text Score:", round(text_score, 2))
    print("Final:", question_score)

    return question_result