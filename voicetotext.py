import sounddevice as sd
from scipy.io.wavfile import write
from faster_whisper import WhisperModel

model = WhisperModel("tiny", device="cpu", compute_type="int8")

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

    return text.lower().strip()


def check_ready(text):
    if "ready" in text:
        print("Welcome to the game! Let's get started.")
        return True
    else:
        print("User said:", text)
        return False 