import sounddevice as sd
import numpy as np
import librosa
from wsServer import send_ws

sample_rate = 16000
block_duration = 0.5
block_size = int(sample_rate * block_duration)

voice_energy_values = []
voice_pitch_values = []
voice_stream = None


def audio_callback(indata, frames, time, status):
    if status:
        print(status)

    audio = indata[:, 0].astype(np.float32)

    rms = np.sqrt(np.mean(audio ** 2))
    energy = min(rms * 5, 1.0)

    pitch = 0

    if energy > 0.02:
        try:
            f0 = librosa.yin(
                audio,
                fmin=80,
                fmax=400,
                sr=sample_rate
            )

            valid_pitch = f0[np.isfinite(f0)]

            if len(valid_pitch) > 0:
                pitch = float(np.median(valid_pitch))

        except Exception as e:
            print("Pitch error:", e)
            pitch = 0

    voice_energy_values.append(float(energy))

    if pitch > 0:
        voice_pitch_values.append(float(pitch))

    avg_energy = sum(voice_energy_values) / len(voice_energy_values)

    if voice_pitch_values:
        avg_pitch = sum(voice_pitch_values) / len(voice_pitch_values)
    else:
        avg_pitch = 0

    send_ws({
        "type": "voice",
        "energy": float(energy),
        "pitch": float(pitch),
        "pitch_average": float(avg_pitch),
        "energy_average": float(avg_energy),
        "score": get_voice_score()
    })

    print(
        "energy:", round(energy, 3),
        "pitch:", round(pitch, 1),
        "avg pitch:", round(avg_pitch, 1)
    )


def start_voice_stream():
    global voice_stream

    if voice_stream is None:
        voice_energy_values.clear()
        voice_pitch_values.clear()

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

    voice_energy_values.clear()
    voice_pitch_values.clear()


def get_voice_score():
    if not voice_energy_values:
        return 0

    avg_energy = sum(voice_energy_values) / len(voice_energy_values)

    if voice_pitch_values:
        avg_pitch = sum(voice_pitch_values) / len(voice_pitch_values)
    else:
        avg_pitch = 0

    pitch_score = min(avg_pitch / 400, 1.0)

    voice_score = (avg_energy * 50) + (pitch_score * 50)

    return max(0, min(100, voice_score))