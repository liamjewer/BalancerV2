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
HMI_DIR = os.path.abspath("hmi")
CONTROL_LOOP_BIN = os.path.abspath("./build/control_loop")
PORT = 11227
HMI_PORT = 3683
CAMERA_PORT = 2609

# timing
LOOP_HZ = 100
LOOP_PERIOD = 1.0 / LOOP_HZ

# states
class State(Enum):
    DISABLED = 0
    STATIONARY = 1
    AUTONOMOUS = 2
    TELEOPERATED = 3

# ----- Globals -----
log = logging.getLogger("robot")


class Robot:
    def __init__(self):
        self.running = False
        self.current_state = State.DISABLED
        self.previous_state = None
        self.control_loop = ControlLoop([CONTROL_LOOP_BIN], core=3)
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
        self.control_loop.start()

        # set up web server
        handler = partial(SimpleHTTPRequestHandler, directory=HMI_DIR)
        self.httpd = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
        # wait for new connections indefinitely on separate thread
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        log.info("Successfully connected - port: %d", PORT)

        #set up websocket comm. server
        self.hmi.start()

        self.control_loop.send("message", "test")


    def periodic(self, dt):
        #check for output from control loop and handle them
        current_ctrl_msg = self.control_loop.get_next_msg()
        while current_ctrl_msg is not None:
            msg_type, value = current_ctrl_msg
           
            match msg_type:
                case "CTRL_OR":
                    log.info(f"[control loop] control loop overrun by {value} ms")
                case _:
                    log.info(value)

            current_ctrl_msg = self.control_loop.get_next_msg()

        # check for hmi messages and handle them
        current_hmi_msg = self.hmi.get_next_msg()

        while current_hmi_msg is not None:
            msg_type, value = current_hmi_msg;
            
            match msg_type:
                case "ESTOP": # safety #1 priority
                    self.control_loop.send("ESTOP", True)
                    time.sleep(0.5) # wait for cpp to register the command before we kill it
                    sys.exit(0)
                case "disable":
                    # set disabled state
                    log.info("disabling")
                    self.current_state = State.DISABLED
                case "enable":
                    # set enabled state
                    log.info("enabling")
                    self.current_state = State.STATIONARY
                case "command":
                    log.info(f"handling command: {value}")
                    self.handle(value)
                case "CTRL_OR":
                    log.info(f"[control loop] control loop overrun by {value} ms")
                case _:
                    log.info(value)

            current_hmi_msg = self.hmi.get_next_msg()

        # handle states
        match self.current_state:
            case State.DISABLED:
                if(self.previous_state != self.current_state):
                    self.disabled_init() # first time so call state init

                self.disabled_periodic()
            case State.STATIONARY:
                if(self.previous_state != self.current_state):
                     self.stationary_init() # first time so call state init

                self.stationary_periodic()
            case State.AUTONOMOUS:
                if(self.previous_state != self.current_state):
                     self.autonomous_init() # first time so call state init

                self.disabled_periodic()
            case State.TELEOPERATED:
                if(self.previous_state != self.current_state):
                     self.teleoperated_init() # first time so call state init

                self.disabled_periodic()
            case _:
                self.current_state = State.DISABLED # default back to disabled

        self.previous_state = self.current_state # reset previous state

    def disabled_init(self):
        self.control_loop.send("disable", True) # pass state to the control loop
        self.hmi.send("state", "DISABLED") # and hmi

    def disabled_periodic(self):
        pass

    def stationary_init(self):
        self.control_loop.send("enable", True) # pass enable signal to the control loop
        self.hmi.send("state", "STATIONARY") # pass state to hmi

    def stationary_periodic(self):
        pass

    def autonomous_init(self):
        self.control_loop.send("enable", True) # pass enable signal to the control loop
        self.hmi.send("state", "AUTONOMOUS")

    def autonomous_periodic():
        pass

    def teleoperated_init(self):
        self.control_loop.send("enable", True) # pass enable signal to the control loop
        self.hmi.send("state", "TELEOPERATED")

    def teleoperated_periodic(self):
        pass

    def handle(self, command):
        match command:
            case "state_stationary":
                self.current_state = State.STATIONARY
            case "state_auto":
                self.current_state = State.AUTONOMOUS
            case "state_teleop":
                self.current_state = State.TELEOPERATED
            case _:
                pass
    
    
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
        self.control_loop.stop()

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