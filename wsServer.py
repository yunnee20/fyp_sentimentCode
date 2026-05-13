import asyncio
import json
import threading
import websockets

connected_clients = set()
loop = None


async def handler(websocket):
    connected_clients.add(websocket)
    print("JS dashboard connected")

    try:
        async for _ in websocket:
            pass
    except:
        pass
    finally:
        connected_clients.remove(websocket)
        print("JS dashboard disconnected")


async def broadcast(data):
    if not connected_clients:
        return

    message = json.dumps(data)

    dead_clients = []

    for client in connected_clients:
        try:
            await client.send(message)
        except:
            dead_clients.append(client)

    for client in dead_clients:
        connected_clients.discard(client)


def send_ws(data):
    global loop

    if loop is None:
        return

    asyncio.run_coroutine_threadsafe(broadcast(data), loop)


async def start_server_async():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()


def start_ws_server():
    global loop

    loop = asyncio.new_event_loop()

    def run():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_server_async())

    thread = threading.Thread(target=run, daemon=True)
    thread.start()