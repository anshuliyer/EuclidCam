import time
import board
import digitalio

class FlashDrive:
    """
    Controls the physical flash hardware via GPIO 16.
    """
    def __init__(self):
        try:
            self.pin = digitalio.DigitalInOut(board.D16)
            self.pin.direction = digitalio.Direction.OUTPUT
            self.pin.value = False
        except Exception as e:
            print(f"[IO] Flash Init failed: {e}")
            self.pin = None

    def trigger(self, duration=1.0):
        """Fires the flash for a specified duration."""
        if self.pin:
            self.pin.value = True
            time.sleep(duration)
            self.pin.value = False
        else:
            print("[STUB] Physical Flash -> ON")
            time.sleep(duration)
            print("[STUB] Physical Flash -> OFF")

    def blip(self, duration=0.1):
        """Quickly blips the physical flash LED."""
        if self.pin:
            try:
                self.pin.value = True
                time.sleep(duration)
                self.pin.value = False
            except Exception as e:
                print(f"[FLASH] Blip error: {e}")
        else:
            print("[STUB] Physical Flash -> BLIP!")
