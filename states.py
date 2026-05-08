from face import start_face_stream, stop_face_stream, get_face_score
from textsentiment import analyze_text_sentiment
from score import calculate_final_score
from voicetotext import voice_to_text, check_ready
from voice_freqpitch import start_voice_stream, stop_voice_stream, get_voice_score

from face import start_face_stream, stop_face_stream, get_face_score


ready = False
startTest = False
startQues = False

def welcome():
    global ready
    print("now playing welcome video and music")
    ready = True


def Ready():
    global startTest

    print("Say ready after the beep...")
    text = voice_to_text(duration=5)

    if check_ready(text):
        startTest = True
        return True

    return False


# def play_question(question_number):
#     print(f"now playing question {question_number} video")

#     # start real-time pitch/energy stream
#     start_voice_stream()

#     # record answer and transcribe
#     answer_text = voice_to_text(duration=10)

#     # stop real-time stream
#     stop_voice_stream()

#     print("Answer:", answer_text)

#     return answer_text



def run_question(question_number):
    print(f"Question {question_number} started")

    # start real-time data to TouchDesigner
    start_face_stream()
    start_voice_stream()

    # record + transcribe while streams are running
    transcript = voice_to_text(duration=10)

    # stop real-time streams
    stop_face_stream()
    stop_voice_stream()

    # get average scores collected during answer
    face_score = get_face_score()
    voice_score = get_voice_score()

    # text score after transcription
    text_result = analyze_text_sentiment(transcript)
    text_score = text_result["text_score"]

    question_score = calculate_final_score(
        face_score=face_score,
        voice_score=voice_score,
        text_score=text_score
    )

    question_result = {
        "question_number": question_number,
        "transcript": transcript,
        "face_score": face_score,
        "voice_score": voice_score,
        **text_result,
        **question_score
    }

    print("------ QUESTION RESULT ------")
    print(question_result)

    return question_result
    print(f"Question {question_number} started")
    start_voice_stream()
    # 1. Capture face snapshot
    face_result = face_trigger(face_start=True, show=True)
    answer_text = voice_to_text(duration=10)
    if face_result is None:
        face_score = 50
    else:
        face_score = face_result["face_score"]

    # 2. Record and transcribe voice
    transcript = voice_to_text(duration=8)

    # 3. Analyse text sentiment
    text_result = analyze_text_sentiment(transcript)
    text_score = text_result["text_score"]

    # 4. Temporary voice score
    # later replace this with real voice score
    voice_score = 60

    # 5. Combine question score
    question_score = calculate_final_score(
        face_score=face_score,
        voice_score=voice_score,
        text_score=text_score
    )

    question_result = {
        "question_number": question_number,
        "transcript": transcript,
        **face_result,
        **text_result,
        **question_score
    }

    print("------ QUESTION RESULT ------")
    print(question_result)

    return question_result