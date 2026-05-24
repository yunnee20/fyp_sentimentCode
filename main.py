# Main entry point for the sentiment analysis system
# Orchestrates the complete workflow:
# 1. Starts WebSocket server for frontend communication
# 2. Runs the interactive scene flow
# 3. Calculates aggregated sentiment scores
# 4. Generates and prints receipt
# 5. Sends results to TouchDesigner

import time
from wsServer import start_ws_server, send_ws
from sceneControl import run_scene_flow
from score import calculate_total_score
from receipt import save_and_print_receipt
from face import close_face_camera
from pythonosc.udp_client import SimpleUDPClient

td_client = SimpleUDPClient("127.0.0.1", 8002) #Ending result 

def main():
    # start JS websocket server
    start_ws_server()

    # give browser time to connect
    time.sleep(1)

    send_ws({
        "type": "state",
        "status": "system_started"
    })

    # run scenes
    results = run_scene_flow()

    print("")
    print("========== ALL RESULTS ==========")
    print(results)

    if not results:
        print("No results collected.")
        return

    # final score
    total_result = calculate_total_score(results)

    print("")
    print("========== FINAL RESULT ==========")
    print(total_result)
    # td_client.send_message(total_result)

    # average face values
    avg_valence = sum(q.get("valence", 0) for q in results) / len(results)
    avg_thinking = sum(q.get("thinking", 0) for q in results) / len(results)
    avg_arousal = sum(q.get("arousal", 0) for q in results) / len(results)
    avg_anxious = sum(q.get("anxious", 0) for q in results) / len(results)

    receipt_data = {
        "score": total_result["final_score"],
        "face": total_result["face_score"],
        "voice": total_result["voice_score"],
        "text": total_result["text_score"],
        "label": total_result["label"].replace('"', '').upper(),
        "authenticity": total_result["authenticity"],

        "valence": round(avg_valence, 2),
        "thinking": round(avg_thinking, 2),
        "arousal": round(avg_arousal, 2),
        "anxious": round(avg_anxious, 2),
    }

    for key, value in receipt_data.items():
        td_client.send_message(f"/receipt/{key}", value)
        

    # print receipt
    save_and_print_receipt(receipt_data)

    close_face_camera()


if __name__ == "__main__":
    main()