from wsServer import start_ws_server
from scene_controller import run_scene_flow

def main():
    start_ws_server()
    run_scene_flow()

if __name__ == "__main__":
    main()