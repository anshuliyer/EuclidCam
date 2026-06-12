import subprocess

class BatteryManagement:
    """
    Manages battery-related state and hardware interfaces.
    """
    def __init__(self):
        self.battery_level = True  # Default to True

    @property
    def is_undervoltage(self) -> bool:
        """
        Checks if the Raspberry Pi input voltage is jittery/low (< 4.63V)
        using the internal vcgencmd throttled state.
        """
        try:
            result = subprocess.run(['vcgencmd', 'get_throttled'], capture_output=True, text=True, timeout=1)
            if "throttled=" in result.stdout:
                hex_str = result.stdout.strip().split('=')[1]
                throttled_val = int(hex_str, 16)
                
                # Bit 0 (0x1) = Under-voltage detected right now
                # Bit 16 (0x10000) = Under-voltage has occurred since boot
                if (throttled_val & 0x1) or (throttled_val & 0x10000):
                    return True
            return False
        except Exception:
            return False

class GPIOTop:
    """
    Manages top-level GPIO hardware settings (e.g. Flash).
    """
    def __init__(self):
        self.flash_setting = True  # Default to True
