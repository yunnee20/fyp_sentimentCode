import cv2
import mediapipe as mp
from pythonosc.udp_client import SimpleUDPClient

#SETUP

client = SimpleUDPClient("127.0.0.1", 8000)

# MediaPipe setup
BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task'),
    output_face_blendshapes=True,
    num_faces=1
)

landmarker = FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

# MAIN LOOP

while True:
    ret, frame = cap.read()
    if not ret:
        break

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=frame
    )

    result = landmarker.detect(mp_image)

    if result.face_blendshapes:
        blendshapes = result.face_blendshapes[0]

        data = {b.category_name: b.score for b in blendshapes}

        brow = data.get("browInnerUp", 0)
        jaw = data.get("jawOpen", 0)
        smile = data.get("mouthSmileLeft", 0)

        print("brow:", brow, "jaw:", jaw, "smile:", smile)

        # send OSC messages
        client.send_message("/face/brow", brow)
        client.send_message("/face/jaw", jaw)
        client.send_message("/face/smile", smile)

    cv2.imshow("cam", frame)

    if cv2.waitKey(1) & 0xFF == 27:

        break

cap.release()
cv2.destroyAllWindows()