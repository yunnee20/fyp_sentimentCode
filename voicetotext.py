import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

model = WhisperModel("base", device="cpu", compute_type="int8")
global transcribed_text
transcribed_text = "ready"

def voice_to_text(duration=5, filename="test_voice.wav"):
    sample_rate = 16000

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

    segments, info = model.transcribe(filename)

    text = ""
    for segment in segments:
        text += segment.text.strip() + " "
    # global transcribed_text
    # transcribed_text = text.lower()
    return text


def check_ready():
    if "ready" in transcribed_text:
        print("Welcome to the game! Let's get started.")
        return True
    else:
        print("User said:", transcribed_text)
        return False 
    
def transcribe_audio_file(filename):
    segments, info = model.transcribe(filename)

    text = ""

    for segment in segments:
        text += segment.text.strip() + " "

    return text.lower().strip()