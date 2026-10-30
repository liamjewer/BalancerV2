import json
import queue
import subprocess
import threading
import time

class ControlLoop:
    def __init__(self, command, core=3):
        self.command = command
        self.core = core # the CPU core reserved for the C++ program (default 3)
        self.incoming = queue.Queue()
        self.proc = None
        self.lock = threading.Lock()

    def start(self):
        cmd = ["taskset", "-c", str(self.core)] + self.command  # pins it to one core
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        for line in self.proc.stdout:   # blocks until a full line arrives
            t_arrival = time.perf_counter_ns()
            try:
                data = json.loads(line)
                self.incoming.put((data["type"], data["value"], t_arrival))
            except (json.JSONDecodeError, KeyError, TypeError):
                pass

    def send(self, msg_type, msg_value):
        data = json.dumps({"type": msg_type, "value": msg_value}) + "\n"
        with self.lock:
            try:
                self.proc.stdin.write(data)
                self.proc.stdin.flush()
            except (BrokenPipeError, ValueError, AttributeError):
                pass  # process is gone or not started
    
    # returns next message and pops it from the queue
    def get_next_msg(self):
        try:
            return self.incoming.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.proc.kill()