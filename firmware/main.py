import logging
import os
import signal
import threading
import time
import subprocess

from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

# custom modules
from hmi_link import HMILink

HMI_DIR = os.path.abspath("../hmi")
PORT = 11227
HMI_PORT = 3683
CAMERA_PORT = 2609

LOOP_HZ = 100
LOOP_PERIOD = 1.0 / LOOP_HZ

log = logging.getLogger("robot")

class Robot:
    def __init__(self):
        self.running = False
        self.httpd = None
        self.hmi = HMILink(HMI_PORT)
        self.current_tick = 0

        self.streamer = subprocess.Popen(
            [
                "ustreamer",
                "--device=/dev/video0",
                "--format=MJPEG",
                "--resolution=854x480",
                "--host=0.0.0.0",
                f"--port={CAMERA_PORT}",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def setup(self):
        log.info("setup")
        
        # set up web server
        handler = partial(SimpleHTTPRequestHandler, directory=HMI_DIR)
        self.httpd = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
        # wait for new connections indefinitely on separate thread
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        log.info("Successfully connected - port: %d", PORT)

        #set up websocket comm. server
        self.hmi.start()


    def periodic(self, dt):
        if self.current_tick%100 == 0 : self.hmi.send("console", str(self.current_tick))


    # log a fault and stop the main loop
    def fault(self, reason):
        log.error("fault: %s", reason)
        self.stop()

    # full shutdown procedure
    def shutdown(self):
        log.info("shutdown")

        # stop web server
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()

    def stop(self):
        self.running = False

    def run(self):
        #startup sequence
        self.setup()
        self.running = True

        # track timing
        last = time.perf_counter()
        next_tick = last

        try:
            while self.running:
                # calculate time since last tick dt
                now = time.perf_counter()
                dt = now - last
                last = now
                self.current_tick += 1

                # pass off to state machine
                self.periodic(dt)

                # itterate tick
                next_tick += LOOP_PERIOD
                delay = next_tick - time.perf_counter()

                # check for overruns
                if delay > 0:
                    time.sleep(delay)
                else:
                    # if overrun occured, log and resync timing
                    log.warning("loop overrun by: %.2fms", delay*1000)
                    next_tick = time.perf_counter() 
        except Exception:
            log.exception("robot runtime error: ")
        finally:
            self.shutdown()


def main():
    #initialize log
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    #initialize robot object
    bv2 = Robot()

    # handle stop conditions for safe shutdown
    signal.signal(signal.SIGINT, lambda *_: bv2.stop())
    signal.signal(signal.SIGTERM, lambda *_: bv2.stop())

    #start robot
    bv2.run()

# standard python main function
if __name__ == "__main__":
    main()