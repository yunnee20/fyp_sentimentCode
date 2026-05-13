from pathlib import Path
import threading
import time
from pythonosc.udp_client import SimpleUDPClient
from wsServer import send_ws

MODEL_PATH = Path(__file__).with_name("face_landmarker.task")

client = SimpleUDPClient("127.0.0.1", 8000)

landmarker = None
cap = None
cv2 = None
mp = None

face_running = False
face_thread = None
face_scores = []

# FACE_POINTS = {
#     "brow_left": 65,
#     "brow_right": 295,
#     "mouth": 13,
#     "jaw": 152,
#     "eye_left": 159,
#     "eye_right": 386,
# }

FACE_POINTS = {
    # brows
    "brow_left_inner": 55,
    "brow_left_mid": 65,
    "brow_left_outer": 105,
    "brow_right_inner": 285,
    "brow_right_mid": 295,
    "brow_right_outer": 334,

    # eyes
    "eye_left_top": 159,
    "eye_left_bottom": 145,
    "eye_left_outer": 33,
    "eye_left_inner": 133,
    "eye_right_top": 386,
    "eye_right_bottom": 374,
    "eye_right_inner": 362,
    "eye_right_outer": 263,

    # mouth
    "mouth_top": 13,
    "mouth_bottom": 14,
    "mouth_left": 61,
    "mouth_right": 291,

    # face / jaw
    "chin": 152,
    "jaw_left": 234,
    "jaw_right": 454,
    "nose": 1,
}


def get_cv2():
    global cv2
    if cv2 is None:
        import cv2 as cv2_module
        cv2 = cv2_module
    return cv2


def get_mediapipe():
    global mp
    if mp is None:
        import mediapipe as mediapipe_module
        mp = mediapipe_module
    return mp


def get_landmarker():
    global landmarker

    if landmarker is None:
        mediapipe = get_mediapipe()

        BaseOptions = mediapipe.tasks.BaseOptions
        FaceLandmarker = mediapipe.tasks.vision.FaceLandmarker
        FaceLandmarkerOptions = mediapipe.tasks.vision.FaceLandmarkerOptions

        options = FaceLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=str(MODEL_PATH)),
            output_face_blendshapes=True,
            num_faces=1
        )

        landmarker = FaceLandmarker.create_from_options(options)

    return landmarker


def get_camera(camera_index=1):
    global cap

    if cap is None or not cap.isOpened():
        cv = get_cv2()
        cap = cv.VideoCapture(camera_index)

    return cap


def calculate_face_values(data):
    valence = (
        data.get("mouthSmileLeft", 0)
        + data.get("mouthSmileRight", 0)
        - data.get("mouthFrownLeft", 0)
        - data.get("mouthFrownRight", 0)
    )

    thinking = (
        data.get("eyeLookUpLeft", 0)
        + data.get("eyeLookUpRight", 0)
    )

    arousal = (
        data.get("jawOpen", 0)
        + data.get("eyeWideLeft", 0)
        + data.get("eyeWideRight", 0)
        + data.get("browInnerUp", 0)
    )

    anxious = (
        data.get("eyeSquintLeft", 0)
        + data.get("eyeSquintRight", 0)
        + data.get("browDownLeft", 0)
        + data.get("browDownRight", 0)
        + data.get("mouthPressLeft", 0)
        + data.get("mouthPressRight", 0)
    )

    valence_percent = max(0, min(100, valence * 100))
    thinking_percent = max(0, min(100, thinking * 100))
    arousal_percent = max(0, min(100, arousal * 100))
    anxious_percent = max(0, min(100, anxious * 100))

    # You can adjust this formula later
    face_score = (
        0.25 * valence_percent
        + 0.25 * arousal_percent
        + 0.25 * thinking_percent
        + 0.25 * anxious_percent
    )

    face_score = max(0, min(100, face_score))

    return {
        "valence": valence_percent,
        "thinking": thinking_percent,
        "arousal": arousal_percent,
        "anxious": anxious_percent,
        "face_score": face_score,
    }


def send_landmarks_to_td(result):
    if not result.face_landmarks:
        return

    landmarks = result.face_landmarks[0]

    for name, idx in FACE_POINTS.items():
        point = landmarks[idx]

        client.send_message(f"/pos/{name}_x", float(point.x))
        client.send_message(f"/pos/{name}_y", float(point.y))


def send_face_values_to_td(values):
    client.send_message("/face/valence", float(values["valence"]))
    client.send_message("/face/thinking", float(values["thinking"]))
    client.send_message("/face/arousal", float(values["arousal"]))
    client.send_message("/face/anxious", float(values["anxious"]))
    client.send_message("/face/score", float(values["face_score"]))


def face_loop(camera_index=1, show=True):
    global face_running, face_scores

    cv = get_cv2()
    mediapipe = get_mediapipe()
    camera = get_camera(camera_index)
    detector = get_landmarker()

    while face_running:
        ret, frame = camera.read()

        if not ret:
            print("Could not read camera frame.")
            time.sleep(0.05)
            continue

        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        mp_image = mediapipe.Image(
            image_format=mediapipe.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = detector.detect(mp_image)

        if result.face_blendshapes:
            blendshapes = result.face_blendshapes[0]
            data = {b.category_name: b.score for b in blendshapes}

            values = calculate_face_values(data)

            


            face_value_history.append(values)
            face_scores.append(values["face_score"])

            send_landmarks_to_td(result)
            send_face_values_to_td(values)

            print(
                "face:",
                round(values["face_score"], 2),
                "valence:",
                round(values["valence"], 2),
                "thinking:",
                round(values["thinking"], 2),
                "arousal:",
                round(values["arousal"], 2),
                "anxious:",
                round(values["anxious"], 2),
            )

        else:
            client.send_message("/face/score", 0)

        if show:
            cv.imshow("Face Camera", frame)
            cv.waitKey(1)

        time.sleep(0.03)


def start_face_stream(camera_index=1, show=True):
    global face_running, face_thread, face_scores, face_value_history

    if face_running:
        print("Face stream already running.")
        return

    face_scores = []
    face_value_history = []
    face_running = True

    face_thread = threading.Thread(
        target=face_loop,
        args=(camera_index, show),
        daemon=True
    )

    face_thread.start()
    print("Face stream started.")


def stop_face_stream():
    global face_running, face_thread

    face_running = False

    if face_thread is not None:
        face_thread.join()
        face_thread = None

    print("Face stream stopped.")


def get_face_score():
    if len(face_scores) == 0:
        return 50

    return sum(face_scores) / len(face_scores)

def face_details_score(valence, thinking, arousal, anxious):
    return valence, thinking, arousal, anxious



def close_face_camera():
    global cap

    if cap is not None:
        cap.release()
        cap = None

    if cv2 is not None:
        cv2.destroyAllWindows()

def get_average_face_values():
    if len(face_value_history) == 0:
        return {
            "valence": 0,
            "thinking": 0,
            "arousal": 0,
            "anxious": 0,
            "face_score": 50
        }

    return {
        "valence": sum(v["valence"] for v in face_value_history) / len(face_value_history),
        "thinking": sum(v["thinking"] for v in face_value_history) / len(face_value_history),
        "arousal": sum(v["arousal"] for v in face_value_history) / len(face_value_history),
        "anxious": sum(v["anxious"] for v in face_value_history) / len(face_value_history),
        "face_score": sum(v["face_score"] for v in face_value_history) / len(face_value_history),
    }