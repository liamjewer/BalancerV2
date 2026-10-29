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
    BUTTON_NAMES = (
        "aButton", "bButton", "xButton", "yButton",
        "leftBumper", "rightBumper",
        "viewButton", "startButton", "xboxButton",
        "leftJoystickPress", "rightJoystickPress",
        "padUp", "padDown", "padLeft", "padRight",
    )
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

    def __init__(self, robot):
        self.robot = robot

    def parse(self, text: str) -> bool:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return False

        if data is None:  # no controller detected by browser
            self.connected = False
            return False

        # capture old button states
        prev = {n: getattr(self, n) for n in self.BUTTON_NAMES}

        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self._fireEvents(prev)

        self.connected = True
        return True

    def _fireEvents(self, prev: dict):
        for name in self.BUTTON_NAMES:
            now = getattr(self, name)
            if now and not prev[name]:
                getattr(self, "on_press_" + name)()
            elif prev[name] and not now:
                getattr(self, "on_release_" + name)()

    # event methods
    
    def on_press_aButton(self): self.robot.handle("lights")
    def on_release_aButton(self): self.robot.handle("lights")
    def on_press_bButton(self): pass
    def on_release_bButton(self): pass
    def on_press_xButton(self): pass
    def on_release_xButton(self): pass
    def on_press_yButton(self): pass
    def on_release_yButton(self): pass
    def on_press_leftBumper(self): pass
    def on_release_leftBumper(self): pass
    def on_press_rightBumper(self): pass
    def on_release_rightBumper(self): pass
    def on_press_viewButton(self): pass
    def on_release_viewButton(self): pass
    def on_press_startButton(self): pass
    def on_release_startButton(self): pass
    def on_press_xboxButton(self): pass
    def on_release_xboxButton(self): pass
    def on_press_leftJoystickPress(self): pass
    def on_release_leftJoystickPress(self): pass
    def on_press_rightJoystickPress(self): pass
    def on_release_rightJoystickPress(self): pass
    def on_press_padUp(self): pass
    def on_release_padUp(self): pass
    def on_press_padDown(self): pass
    def on_release_padDown(self): pass
    def on_press_padLeft(self): pass
    def on_release_padLeft(self): pass
    def on_press_padRight(self): pass
    def on_release_padRight(self): pass