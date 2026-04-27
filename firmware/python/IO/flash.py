import time
try:
    import gpiod
    from gpiod.line import Direction, Value
except ImportError:
    gpiod = None

class FlashDrive:
    """
    Controls the physical flash hardware via GPIO 21.
    """
    def __init__(self, pin=21):
        self.pin = pin
        self.chip = None
        self.line_request = None
        
        if gpiod:
            try:
                # Assuming chip 0 (standard for RPi)
                self.chip = gpiod.Chip("/dev/gpiochip4") # RPi 5 usually uses gpiochip4 for header pins
                self.line_request = self.chip.request_lines(
                    config={self.pin: gpiod.LineSettings(direction=Direction.OUTPUT)}
                )
            except Exception as e:
                print(f"[IO] GPIO Init failed: {e}")

    def pin_21_drive(self, state: bool):
        """Sets the state of GPIO 21."""
        if self.line_request:
            val = Value.ACTIVE if state else Value.INACTIVE
            self.line_request.set_value(self.pin, val)
        else:
            print(f"[STUB] Pin 21 -> {'ON' if state else 'OFF'}")

    def trigger(self, duration=0.5):
        """Fires the flash for a specified duration."""
        self.pin_21_drive(True)
        time.sleep(duration)
        self.pin_21_drive(False)
