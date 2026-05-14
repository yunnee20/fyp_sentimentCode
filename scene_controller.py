import random
import keyboard
from wsServer import send_ws
from pythonosc.udp_client import SimpleUDPClient

td_client = SimpleUDPClient("127.0.0.1", 8000)

SCENES = [1, 2, 3, 4, 5, 6]

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


def run_scene_flow():
    remaining_scenes = SCENES.copy()

    send_state("welcome")

    print("Press ENTER to start.")
    wait_for_key(["enter"])

    send_state("begin_audio")

    while remaining_scenes:
        scene = random.choice(remaining_scenes)
        remaining_scenes.remove(scene)

        send_state("scene", scene)

        print(f"Playing scene {scene}.")
        print("Press A/B/C/D after scene ends.")

        choice = wait_for_key(["a", "b", "c", "d", "esc"])

        if choice == "esc":
            break

        send_state("response_received", scene)

        print("Choice:", choice)
        print("Press SPACE to continue, TAB to skip, ESC to end.")

        next_key = wait_for_key(["space", "tab", "esc"])

        if next_key == "esc":
            break

        if next_key == "tab":
            print("Skipped justification.")

        if next_key == "space":
            print("Continue to next scene.")

    send_state("ending")
    print("Experience ended.")