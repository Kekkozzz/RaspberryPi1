from gpiozero import LED, Buzzer


class Actuators:
    def __init__(self, pins: dict):
        self.led_red = LED(pins["led_red"])
        self.led_green = LED(pins["led_green"])
        self.led_blue = LED(pins["led_blue"])
        self.buzzer = Buzzer(pins["buzzer"])
        self._leds = {
            "red": self.led_red,
            "green": self.led_green,
            "blue": self.led_blue,
        }

    def all_off(self):
        for led in self._leds.values():
            led.off()
        self.buzzer.off()

    def set_led(self, color: str, on: bool):
        if color not in self._leds:
            raise ValueError(f"Unknown LED color: {color}. Use: {list(self._leds.keys())}")
        if on:
            self._leds[color].on()
        else:
            self._leds[color].off()

    def buzzer_on(self):
        self.buzzer.on()

    def buzzer_off(self):
        self.buzzer.off()

    def set_state(self, state: str):
        """Set actuators to match the given system state."""
        self.all_off()
        if state == "IDLE":
            self.led_green.blink(on_time=1, off_time=1)
        elif state == "ARMED":
            self.led_green.on()
        elif state == "ALERT":
            self.led_blue.blink(on_time=0.3, off_time=0.3)
        elif state == "CHALLENGE":
            self.led_blue.on()
            self.buzzer.beep(on_time=0.1, off_time=0.9)  # soft countdown warning
        elif state == "DISARMED":
            self.led_green.blink(on_time=0.2, off_time=0.2)
            self.buzzer.beep(on_time=0.05, off_time=0.05, n=3)  # success tone
        elif state == "ALARM":
            self.led_red.on()
            self.buzzer.on()

    def cleanup(self):
        self.all_off()
        self.led_red.close()
        self.led_green.close()
        self.led_blue.close()
        self.buzzer.close()
