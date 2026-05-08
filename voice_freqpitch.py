import sounddevice as sd
import numpy as np
import librosa
from pythonosc.udp_client import SimpleUDPClient

client = SimpleUDPClient("127.0.0.1", 8000)

sample_rate = 16000
block_duration = 0.5
block_size = int(sample_rate * block_duration)

voice_stream = None

def audio_callback(indata, frames, time, status):
    audio = indata[:, 0].astype(np.float32)

    rms = np.sqrt(np.mean(audio ** 2))
    energy = min(rms * 20, 1.0)

    try:
        f0 = librosa.yin(audio, fmin=80, fmax=400, sr=sample_rate)
        pitch = float(np.median(f0))

        if energy < 0.02:
            pitch = 0
    except:
        pitch = 0

    pitch_norm = np.clip((pitch - 80) / (400 - 80), 0, 1) if pitch > 0 else 0

    client.send_message("/voice/energy", float(energy))
    client.send_message("/voice/pitch", float(pitch))
    client.send_message("/voice/pitch_norm", float(pitch_norm))

    print("energy:", round(energy, 3), "pitch:", round(pitch, 1))


def start_voice_stream():
    global voice_stream

    if voice_stream is None:
        voice_stream = sd.InputStream(
            channels=1,
            samplerate=sample_rate,
            blocksize=block_size,
            callback=audio_callback
        )
        voice_stream.start()
        print("Voice stream started")


def stop_voice_stream():
    global voice_stream

    if voice_stream is not None:
        voice_stream.stop()
        voice_stream.close()
        voice_stream = None
        print("Voice stream stopped")