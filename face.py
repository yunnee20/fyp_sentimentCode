from pathlib import Path
from pythonosc.udp_client import SimpleUDPClient

#SETUP

client = SimpleUDPClient("127.0.0.1", 8000)

# SETUP

MODEL_PATH = Path(__file__).with_name("face_landmarker.task")

landmarker = None
cap = None
capture_now = False
cv2 = None
mp = None


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


def trigger_face(face_start=True):
    global capture_now

    if face_start:
        capture_now = True
        print("Capture triggered")
        return True

    capture_now = False
    return False


def face_trigger(face_start=True, voice_score=60, text_score=65, camera_index=1, show=True):
    global capture_now

    if face_start:
        trigger_face(True)

    camera = get_camera(camera_index)
    ret, frame = camera.read()
    if not ret:
        print("Could not read from camera.")
        return None

    result_data = None

    if capture_now:
        capture_now = False  # reset flag

        cv = get_cv2()
        mediapipe = get_mediapipe()
        rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        mp_image = mediapipe.Image(
            image_format=mediapipe.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = get_landmarker().detect(mp_image)

        if result.face_blendshapes:
            blendshapes = result.face_blendshapes[0]
            data = {b.category_name: b.score for b in blendshapes}

            # ----------------------------
            # STATES
            # ----------------------------
            valence = data.get("mouthSmileLeft", 0) + data.get("mouthSmileRight", 0) - data.get("mouthFrownLeft", 0) - data.get("mouthFrownRight", 0)
            thinking = data.get("eyeLookUpLeft", 0) + data.get("eyeLookUpRight", 0)
            arousal = data.get("jawOpen", 0) + data.get("eyeWideLeft", 0) + data.get("eyeWideRight", 0) + data.get("browInnerUp", 0)
            anxious = data.get("eyeSquintLeft", 0) + data.get("eyeSquintRight", 0) + data.get("browDownLeft", 0) + data.get("browDownRight", 0) + data.get("mouthPressLeft", 0) + data.get("mouthPressRight", 0)
            stability = 0.5

            # convert to percentage 
            valence_percent = max(0, min(100, valence * 100))
            thinking_percent = max(0, min(100, thinking * 100)) 
            arousal_percent = max(0, min(100, arousal * 100))
            anxious_percent = max(0, min(100, anxious * 100))
            stability_percent = max(0, min(100, stability * 100))

            # get suboptimal results 
            score = 0.25*valence_percent + 0.25*arousal_percent + 0.2*thinking_percent + 0.2*anxious_percent + 0.1*stability_percent
            score_percent = max(0, min(100, score))

            result_data = {
                "valence": valence_percent,
                "thinking": thinking_percent,
                "arousal": arousal_percent,
                "anxious": anxious_percent,
                "stability": stability_percent,
                "face_score": score_percent,
            }
        else:
            print("No face detected.")

    if show:
        cv = get_cv2()
        cv.imshow("cam", frame)
        cv.waitKey(1)

    return result_data

FACE_POINTS = {
    "brow_left": 65,
    "brow_right": 295,
    "mouth": 13,
    "jaw": 152,
    "eye_left": 159,
    "eye_right": 386,
}

def send_face_to_td(result, data, face_score):
    landmarks = result.face_landmarks[0]

    for name, idx in FACE_POINTS.items():
        p = landmarks[idx]
        client.send_message(f"/pos/{name}_x", float(p.x))
        client.send_message(f"/pos/{name}_y", float(p.y))

    client.send_message("/face/valence", float(data["valence"]))
    client.send_message("/face/thinking", float(data["thinking"]))
    client.send_message("/face/arousal", float(data["arousal"]))
    client.send_message("/face/anxious", float(data["anxious"]))
    client.send_message("/face/score", float(face_score))

def close_face_camera():
    global cap

    if cap is not None:
        cap.release()
        cap = None
    if cv2 is not None:
        cv2.destroyAllWindows()
