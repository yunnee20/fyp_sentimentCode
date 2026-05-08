from voicetotext import voice_to_text, check_ready
from voice_freqpitch import start_voice_stream, stop_voice_stream

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


def play_question(question_number):
    print(f"now playing question {question_number} video")

    # start real-time pitch/energy stream
    start_voice_stream()

    # record answer and transcribe
    answer_text = voice_to_text(duration=10)

    # stop real-time stream
    stop_voice_stream()

    print("Answer:", answer_text)

    return answer_text