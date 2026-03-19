from gpiozero import DigitalInputDevice, Button


class SensorManager:
    def __init__(self, pins: dict, sensor_config: dict):
        self.pir = (
            DigitalInputDevice(pins["pir"], pull_up=False)
            if sensor_config.get("pir_enabled", True)
            else None
        )
        self.light = (
            DigitalInputDevice(pins["light"], pull_up=True)
            if sensor_config.get("light_enabled", True)
            else None
        )
        self.sound = (
            DigitalInputDevice(pins["sound"], pull_up=True)
            if sensor_config.get("sound_enabled", True)
            else None
        )
        self.button_a = Button(pins["button_a"], pull_up=True, bounce_time=0.05)
        self.button_b = Button(pins["button_b"], pull_up=True, bounce_time=0.05)

        self._sensors = []
        if self.pir:
            self._sensors.append(("pir", self.pir))
        if self.light:
            self._sensors.append(("light", self.light))
        if self.sound:
            self._sensors.append(("sound", self.sound))

    def check_sensors(self) -> str | None:
        """Check all enabled sensors. Returns name of first triggered sensor, or None."""
        for name, sensor in self._sensors:
            if sensor.value:
                return name
        return None

    def cleanup(self):
        for _, sensor in self._sensors:
            sensor.close()
        self.button_a.close()
        self.button_b.close()
