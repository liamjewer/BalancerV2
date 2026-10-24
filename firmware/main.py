import logging
import os
import signal
import threading
import time
import subprocess
import sys

from enum import Enum
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from control_loop_link import ControlLoop

# custom modules
from hmi_link import HMILink

# ----- CONSTANTS -----

# communication
HMI_DIR = os.path.abspath("../hmi")
PORT = 11227
HMI_PORT = 3683
CAMERA_PORT = 2609

# timing
LOOP_HZ = 100
LOOP_PERIOD = 1.0 / LOOP_HZ

log = logging.getLogger("robot")
control_loop = ControlLoop(["./control_loop"], core=3)

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

        # start control loop communication
        control_loop.start()

        # set up web server
        handler = partial(SimpleHTTPRequestHandler, directory=HMI_DIR)
        self.httpd = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
        # wait for new connections indefinitely on separate thread
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        log.info("Successfully connected - port: %d", PORT)

        #set up websocket comm. server
        self.hmi.start()

        control_loop.send("message", "test");


    def periodic(self, dt):
        # check for hmi messages and handle them
        current_msg = self.hmi.get_next_msg()
        #check for output from control loop
        msg = control_loop.get_next_msg()
        while msg is not None:
            msg_type, value = msg
            log.info("[control_loop] %s: %s", msg_type, value)
            msg = control_loop.get_next_msg()

        while current_msg is not None:
            match current_msg[0]: # type
                case "ESTOP": # safety #1 priority
                    sys.exit(0)
                case "disable":
                    # set disabled state
                    log.info("disabling");
                case "enable":
                    # set enabled state
                    log.info("enabling");
                case "command":
                    # add command to command queue
                    log.info("commanding");
                case _:
                    log.info(current_msg[1]); #value

            current_msg = self.hmi.get_next_msg()


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

        # kill camera feed
        if self.streamer:
            self.streamer.kill()
            self.streamer.wait()


        # kill control loop
        control_loop.stop()

        #power off the pi
        #subprocess.Popen(["shutdown", "-h", "now"])

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