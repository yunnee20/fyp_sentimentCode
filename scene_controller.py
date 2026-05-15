import random
import time
from sceneOptions import OPTIONS
import keyboard
from textsentiment import analyze_text_sentiment
from wsServer import send_ws
from pythonosc.udp_client import SimpleUDPClient
from audioTrigger import play_audio
from face import start_face_stream, stop_face_stream, get_average_face_values
from voice_freqpitch import start_voice_stream, stop_voice_stream, get_voice_score, start_justification_recording, stop_justification_recording

td_client = SimpleUDPClient("127.0.0.1", 8001)

SCENES = [1, 2, 3, 4, 5, 6]
SCENE_DURATIONS = {
    1: 10,
    2: 10,
    3: 10,
    4: 10,
    5: 10,
    6: 10,
}

def send_state(state, scene=None):
    print("STATE:", state, "SCENE:", scene)

    td_client.send_message("/state/current", state)

    if scene is not None:
        td_client.send_message("/state/scene", scene)

    send_ws({
        "type": "state",
        "status": state,
        "scene": scene
    })


def wait_for_key(valid_keys):
    while True:
        event = keyboard.read_event()

        if event.event_type == keyboard.KEY_DOWN:
            key = event.name.lower()

            if key in valid_keys:
                return key

def choose_response(scene_id):
    print("Choose A/B/C/D, or ESC to end.")

    key = wait_for_key(["a", "b", "c", "d", "esc"])

    if key == "esc":
        return None, None, None

    choice = key.upper()
    selected_text = OPTIONS[scene_id][choice]

    text_result = analyze_text_sentiment(selected_text)

    print("Choice:", choice)
    print("Selected text:", selected_text)
    print("Text sentiment:", text_result)

    send_ws({
        "type": "choice",
        "scene": scene_id,
        "choice": choice,
        "selected_text": selected_text,
        "text_result": text_result
    })
    return choice, selected_text, text_result


def run_scene_flow():
    remaining_scenes = SCENES.copy()
    results = []

    send_video(0)

    print("Press ENTER when audience is ready.")
    wait_for_key(["enter"])

    # later play ready audio here
    play_audio("audio/perfect.mp3", wait=True)

    while remaining_scenes:
        scene_id = random.choice(remaining_scenes)
        remaining_scenes.remove(scene_id)

        send_video(scene_id)

        # temporary wait while scene video plays
        time.sleep(3)

        # start live analysis during answer phase
        start_face_stream(camera_index=1, show=False)
        start_voice_stream()

        choice, selected_text, text_result = choose_response(scene_id)

        if choice is None:
            stop_face_stream()
            stop_voice_stream()
            break

        justification_text, should_end = handle_justification()

        stop_face_stream()
        stop_voice_stream()

        if should_end:
            break

        face_values = get_average_face_values()
        face_score = face_values["face_score"]
        voice_score = get_voice_score()

        # later play response received audio here
        play_audio("audio/response.mp3", wait=True)
        result = {
            "scene": scene_id,
            "choice": choice,
            "selected_text": selected_text,
            "justification_text": justification_text,

            "valence": round(face_values["valence"], 2),
            "thinking": round(face_values["thinking"], 2),
            "arousal": round(face_values["arousal"], 2),
            "anxious": round(face_values["anxious"], 2),

            "face_score": round(face_score, 2),
            "voice_score": round(voice_score, 2),

            "text_score": text_result["text_score"],
            "text_label": text_result["label"],
            "text_result": text_result
        }

        results.append(result)

        print("Saved scene result:", result)

        print("Press SPACE for next scene, ESC to end.")
        next_key = wait_for_key(["space", "esc"])

        if next_key == "esc":
            break

    send_video(7)

    return results

def send_video(index):
    td_client.send_message("/td/video_index", int(index))
    td_client.send_message("/td/video_pulse", 1)

def handle_justification():
    print("Hold SPACE to speak justification.")
    print("Release SPACE to stop.")
    print("Press TAB to skip.")
    print("Press ESC to end.")

    while True:
        event = keyboard.read_event()

        if event.event_type == keyboard.KEY_DOWN:
            key = event.name.lower()

            if key == "tab":
                print("Justification skipped.")
                return "", False

            if key == "esc":
                print("Ending requested.")
                return "", True

            if key == "space":
                start_justification_recording()

                while True:
                    release_event = keyboard.read_event()

                    if (
                        release_event.event_type == keyboard.KEY_UP
                        and release_event.name.lower() == "space"
                    ):
                        justification_text = stop_justification_recording()
                        return justification_text, False