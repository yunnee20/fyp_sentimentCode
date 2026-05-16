import random
import time
import keyboard
from pythonosc.udp_client import SimpleUDPClient
from audioTrigger import play_audio
from sceneOptions import OPTIONS
from textsentiment import analyze_text_sentiment
from wsServer import send_ws

from face import (
    start_face_stream,
    stop_face_stream,
    get_average_face_values
)

from voice_freqpitch import (
    start_voice_stream,
    stop_voice_stream,
    get_voice_score,
    get_voice_values,
    start_justification_recording,
    stop_justification_recording
)

# --------------------
# TD OSC
# --------------------
td_client = SimpleUDPClient("127.0.0.1", 8000)

# --------------------
# SCENE SETTINGS
# --------------------
SCENES = [1, 2, 3, 4, 5, 6]

VIDEO_WELCOME = 0
VIDEO_ENDING = 7

# temporary testing duration
SCENE_WAIT_SECONDS = 3


def send_video(index):
    td_client.send_message("/td/video_index", int(index))
    td_client.send_message("/td/video_pulse", 1)

    send_ws({
        "type": "state",
        "status": "video_playing",
        "video_index": index
    })


def wait_for_key(valid_keys):
    while True:
        event = keyboard.read_event()

        if event.event_type == keyboard.KEY_DOWN:
            key = event.name.lower()

            if key in valid_keys:
                return key


def choose_response(scene_id):
    send_log("Choose A/B/C/D, or ESC to end.")

    send_ws({
        "type": "state",
        "status": "waiting_for_choice",
        "scene": scene_id
    })

    key = wait_for_key(["a", "b", "c", "d", "esc"])

    if key == "esc":
        return None, None, None

    choice = key.upper()
    selected_text = OPTIONS[scene_id][choice]

    text_result = analyze_text_sentiment(selected_text)
    text_score = text_result["text_score"]

    send_log("Choice:", choice)
    send_log("Selected text:", selected_text)
    send_log("Text sentiment:", text_result)

    send_ws({
        "type": "choice",
        "scene": scene_id,
        "choice": choice,
        "selected_text": selected_text
    })

    send_ws({
        "type": "text",
        "transcript": selected_text,
        "label": text_result["label"],
        "joy": text_result.get("joy", 0),
        "sadness": text_result.get("sadness", 0),
        "anger": text_result.get("anger", 0),
        "fear": text_result.get("fear", 0),
        "surprise": text_result.get("surprise", 0),
        "neutral": text_result.get("neutral", 0),
        "disgust": text_result.get("disgust", 0),
        "score": text_result["text_score"]
    })

    return choice, selected_text, text_result


def handle_justification():
    send_log("Hold SPACE to speak justification.")
    send_log("Release SPACE to stop.")
    send_log("Press TAB to skip.")
    send_log("Press ESC to end.")

    send_ws({
        "type": "state",
        "status": "waiting_for_justification"
    })

    while True:
        event = keyboard.read_event()

        if event.event_type == keyboard.KEY_DOWN:
            key = event.name.lower()

            if key == "tab":
                send_log("Justification skipped.")

                send_ws({
                    "type": "state",
                    "status": "justification_skipped"
                })

                return "", False

            if key == "esc":
                send_log("Ending requested.")

                send_ws({
                    "type": "state",
                    "status": "ending_requested"
                })

                return "", True

            if key == "space":
                start_justification_recording()

                send_ws({
                    "type": "state",
                    "status": "justification_recording"
                })

                while True:
                    release_event = keyboard.read_event()

                    if (
                        release_event.event_type == keyboard.KEY_UP
                        and release_event.name.lower() == "space"
                    ):
                        justification_text = stop_justification_recording()

                        send_ws({
                            "type": "justification",
                            "text": justification_text
                        })

                        return justification_text, False



def run_scene_flow():
    
    remaining_scenes = SCENES.copy()
    results = []
    question = 0
    # --------------------
    # WELCOME
    # --------------------
    send_video(VIDEO_WELCOME)

    send_log("Press ENTER when audience is ready.")

    send_ws({
        "type": "state",
        "status": "welcome"
    })

    wait_for_key(["enter"])

    send_ws({
        "type": "state",
        "status": "ready_pressed"
    })

    # optional: play Python overlay audio here later
    play_audio("audio/perfect.mp3")

    # --------------------
    # SCENES
    # --------------------
    while remaining_scenes:
        scene_id = random.choice(remaining_scenes)
        remaining_scenes.remove(scene_id)

        print("")
        print("---------- SCENE", scene_id, "----------")
        
        question += 1
        send_log(f"QUESTION: {question}")
        send_ws({
            "type": "state",
            "status": "question_started",
            "question": question,
            "scene": scene_id
        })

        send_video(scene_id)

        # temporary wait for video
        time.sleep(SCENE_WAIT_SECONDS)

        # --------------------
        # ANSWER PHASE START
        # --------------------
        start_face_stream(camera_index=1, show=False)
        start_voice_stream()

        choice = None
        selected_text = None
        text_result = None
        justification_text = ""
        should_end = False

        try:
            choice, selected_text, text_result = choose_response(scene_id)

            if choice is None:
                should_end = True
            else:
                # optional: play Python overlay audio here later
                play_audio("audio/response.mp3")

                justification_text, should_end = handle_justification()

        finally:
            stop_face_stream()
            stop_voice_stream()

        if choice is None:
            break

        # --------------------
        # COLLECT SCORES
        # --------------------
        face_values = get_average_face_values()
        voice_values = get_voice_values()

        face_score = face_values["face_score"]
        voice_score = get_voice_score()
        text_score = text_result["text_score"]

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
            "text_score": round(text_score, 2),

            "energy_average": round(voice_values["energy_average"], 4),
            "pitch_average": round(voice_values["pitch_average"], 2),

            "text_label": text_result["label"],
            "text_result": text_result
        }

        # log_terminal(result)

        results.append(result)

        send_log("Saved result:", result)

        send_ws({
            "type": "scene_result",
            "result": result
        })

        if should_end:
            break

        send_log("Press ENTER for next scene, ESC to end.")

        send_ws({
            "type": "state",
            "status": "waiting_next_scene"
        })

        next_key = wait_for_key(["enter", "esc"])

        if next_key == "esc":
            break

    # --------------------
    # ENDING
    # --------------------
    send_video(VIDEO_ENDING)

    send_ws({
        "type": "state",
        "status": "ending",
        "results": results
    })

    send_log("Experience ended.")
    return results

def send_log(message):
    print(message)
    send_ws({
        "type": "log",
        "message": str(message)
    })