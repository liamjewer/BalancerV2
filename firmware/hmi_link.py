import asyncio
import json
import queue
import threading
import time

from websockets.asyncio.server import serve, broadcast

class HMILink:
    def __init__(self, port=3683):
        self.port = port
        self.clients = set()
        self.incomming = queue.Queue()
        self.loop = None

    async def _handler(self, websocket):
        self.clients.add(websocket)
        try:
            async for raw in websocket:
                # test if the message is valid JSON
                try:
                    # adds the link to the message queue
                    self.incomming.put(json.loads(raw))
                except json.JSONDecodeError:
                    pass
        finally:
            # clean up on exit
            self.clients.discard(websocket)

    def start(self):
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run, daemon=True).start() # start running self on separate thread

    # runs on communication thread
    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._serve()) # 

    async def _serve(self):
        async with serve(self._handler, "0.0.0.0", self.port):
            await asyncio.Future()   # run forever on specified port

    # sends a message to the HMI
    def send(self, msg_type, msg_value):
        #put the message into json format
        message = {"type": msg_type, "value": msg_value}

        data = json.dumps(message)
        self.loop.call_soon_threadsafe(broadcast, self.clients, data) # broadcast to all clients

    def get_next_msg(self):
        if not self.incomming.empty():
            return self.incomming.get_nowait()
        else:
            return None

hmi = HMILink()
hmi.start()

time.sleep(5)

hmi.send("console", "sent from B-V2")

while True:
    while (msg := hmi.get_next_msg()) is not None:
        print(msg)
    time.sleep(0.01)