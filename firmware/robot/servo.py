import RPi.GPIO as GPIO


class Servo:
    FREQ_HZ = 50
    PERIOD_MS = 1000 / FREQ_HZ  # 20 ms

    def __init__(self, pin, min_ms, max_ms):
        self.pin = pin
        self.min_ms = min_ms
        self.max_ms = max_ms
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)
        self._pwm = GPIO.PWM(pin, self.FREQ_HZ)
        self._pwm.start(0)  # no pulses until the first move

    def go_to(self, angle):
        angle = max(0.0, min(180.0, angle))
        pulse_ms = self.min_ms + (angle / 180.0) * (self.max_ms - self.min_ms)
        self._pwm.ChangeDutyCycle(pulse_ms / self.PERIOD_MS * 100)

    def coast(self):
        self._pwm.ChangeDutyCycle(0)  # stop pulses, servo goes limp

    def close(self):
        self._pwm.stop()