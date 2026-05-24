import sounddevice as sd
import numpy as np
import librosa
import tempfile
import os
from scipy.io.wavfile import write
from faster_whisper import WhisperModel
from wsServer import send_ws

# --------------------
# SETTINGS
# --------------------
sample_rate = 16000
block_duration = 0.5
block_size = int(sample_rate * block_duration)

# --------------------
# WHISPER MODEL
# --------------------
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# --------------------
# GLOBAL STATE
# --------------------
voice_energy_values = []
voice_pitch_values = []
voice_stream = None

recording_justification = False
justification_chunks = []


def audio_callback(indata, frames, time, status):
    global recording_justification, justification_chunks

    if status:
        print(status)

    audio = indata[:, 0].astype(np.float32)

    # --------------------
    # RECORD JUSTIFICATION IN MEMORY ONLY
    # --------------------
    if recording_justification:
        justification_chunks.append(indata.copy())

    # --------------------
    # ENERGY
    # --------------------
    rms = np.sqrt(np.mean(audio ** 2))
    energy = min(rms * 5, 1.0)

    # --------------------
    # PITCH
    # --------------------
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

    # --------------------
    # STORE VALUES FOR SCORE
    # --------------------
    voice_energy_values.append(float(energy))

    if pitch > 0:
        voice_pitch_values.append(float(pitch))

    avg_energy = sum(voice_energy_values) / len(voice_energy_values)

    if voice_pitch_values:
        avg_pitch = sum(voice_pitch_values) / len(voice_pitch_values)
    else:
        avg_pitch = 0

    # --------------------
    # SEND TO JS PANEL
    # --------------------
    send_ws({
        "type": "voice",
        "energy": float(energy),
        "pitch": float(pitch),
        "pitch_average": float(avg_pitch),
        "energy_average": float(avg_energy),
        "score": get_voice_score()
    })




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
    global voice_stream, recording_justification, justification_chunks

    if recording_justification:
        recording_justification = False
        justification_chunks = []

    if voice_stream is not None:
        voice_stream.stop()
        voice_stream.close()
        voice_stream = None
        print("Voice stream stopped")


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


def get_voice_values():
    if not voice_energy_values:
        return {
            "energy_average": 0,
            "pitch_average": 0,
            "voice_score": 0
        }

    avg_energy = sum(voice_energy_values) / len(voice_energy_values)

    if voice_pitch_values:
        avg_pitch = sum(voice_pitch_values) / len(voice_pitch_values)
    else:
        avg_pitch = 0

    return {
        "energy_average": avg_energy,
        "pitch_average": avg_pitch,
        "voice_score": get_voice_score()
    }


def start_justification_recording():
    global recording_justification, justification_chunks

    justification_chunks = []
    recording_justification = True

    send_ws({
        "type": "state",
        "status": "justification_recording"
    })

    print("Justification recording started.")


def stop_justification_recording():
    global recording_justification, justification_chunks

    recording_justification = False

    if len(justification_chunks) == 0:
        print("No justification audio recorded.")

        send_ws({
            "type": "text",
            "transcript": "",
            "label": "none",
            "sentiment": 0,
            "score": 0
        })

        return ""

    audio = np.concatenate(justification_chunks, axis=0)

    # convert float audio to int16
    audio_int16 = (audio * 32767).astype(np.int16)

    justification_text = transcribe_audio_array(
        audio_int16,
        sample_rate,
        whisper_model
    )

    # clear raw audio from memory
    justification_chunks = []

    send_ws({
        "type": "text",
        "transcript": justification_text
    })

    print("Justification transcript:", justification_text)

    return justification_text


def transcribe_audio_array(audio_int16, sample_rate, model):
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        write(temp_path, sample_rate, audio_int16)

        segments, info = model.transcribe(temp_path)

        text = ""

        for segment in segments:
            text += segment.text.strip() + " "

        return text.lower().strip()

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)