import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

# ------------
global transcribed_text
transcribed_text = ""

def voicetotext(): 
    global transcribed_text
    # --------------------
    # SETTINGS
    # --------------------
    duration = 5          # seconds to record
    sample_rate = 16000
    filename = "test_voice.wav"

    # --------------------
    # LOAD MODEL
    # --------------------
    model = WhisperModel("tiny", device="cpu", compute_type="int8") #base or tiny

    print("Press ENTER to start recording...")
    input()

    print("Recording...")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="int16"
    )
    sd.wait()

    write(filename, sample_rate, audio)
    print("Recording saved.")

    # --------------------
    # TRANSCRIBE
    # --------------------
    segments, info = model.transcribe(filename)

    text = ""

    for segment in segments:
        text += segment.text.strip() + " "

    transcribed_text = text.lower()
    # print("InVTdef:",transcribed_text)
    return transcribed_text 

def readyText(r):
    # print("In readyText:", transcribed_text)
    if "ready" in transcribed_text:
        r = True
        print("Welcome to the game! Let's get started.")
        return r
    else:
        r = False
        print(transcribed_text)
        return r