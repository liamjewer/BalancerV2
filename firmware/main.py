import logging
import os
import signal
import threading
import time
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

HMI_DIR = os.path.abspath("hmi")
PORT = 11227

LOOP_HZ = 100
LOOP_PERIOD = 1.0 / LOOP_HZ

log = logging.getLogger("robot")

class Robot:
    def __init__(self):
        self.running = False
        self.httpd = None

    # ---- lifecycle ----

    def setup(self):
        log.info("setup")
        handler = partial(SimpleHTTPRequestHandler, directory=HMI_DIR)
        self.httpd = ThreadingHTTPServer(("0.0.0.0", PORT), handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        log.info("Successfully connected - port: %d", PORT)

    def update(self, dt):
        pass

    def fault(self, reason):
        log.error("fault: %s", reason)
        self.stop()

    def shutdown(self):
        log.info("shutdown")

        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()

    # ---- main loop ----

    def run(self):
        self.setup()
        self.running = True
        last = time.perf_counter()
        next_tick = last

        try:
            while self.running:
                now = time.perf_counter()
                dt = now - last
                last = now

                self.update(dt)

                # sleep until the next tick; if we overran, skip the sleep and resync
                next_tick += LOOP_PERIOD
                delay = next_tick - time.perf_counter()
                if delay > 0:
                    time.sleep(delay)
                else:
                    next_tick = time.perf_counter()
        except Exception:
            log.exception("loop error: ")
        finally:
            self.shutdown()

    def stop(self):
        self.running = False


def main():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s")
    bv2 = Robot()

    # handle stop conditions for safe shutdown
    signal.signal(signal.SIGINT, lambda *_: bv2.stop())
    signal.signal(signal.SIGTERM, lambda *_: bv2.stop())

    #start robot
    bv2.run()


if __name__ == "__main__":
    main()