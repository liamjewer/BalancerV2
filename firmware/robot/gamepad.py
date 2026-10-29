import json
import time
from dataclasses import dataclass


@dataclass
class Gamepad:
    # axes and triggers (raw floats)
    leftJoystickX: float = 0.0
    leftJoystickY: float = 0.0
    rightJoystickX: float = 0.0
    rightJoystickY: float = 0.0
    leftTrigger: float = 0.0
    rightTrigger: float = 0.0

    # buttons (raw booleans)
    aButton: bool = False
    bButton: bool = False
    xButton: bool = False
    yButton: bool = False
    leftBumper: bool = False
    rightBumper: bool = False
    viewButton: bool = False
    startButton: bool = False
    leftJoystickPress: bool = False
    rightJoystickPress: bool = False
    xboxButton: bool = False
    padUp: bool = False
    padDown: bool = False
    padLeft: bool = False
    padRight: bool = False

    # link state
    connected: bool = False

    def parse(self, text: str) -> bool:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return False

        if data is None:  # no controller detected by browser
            self.connected = False
            return False

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.connected = True
        return True