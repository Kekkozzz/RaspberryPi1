import random
import sys
import select
import threading
import time
import logging

logger = logging.getLogger("sentinelpi.simulator")


class Simulator:
    """Provides simulated sensor triggers and keyboard button input for development without hardware."""

    def __init__(self, sensors, trigger_interval: float = 10.0):
        self.sensors = sensors
        self.trigger_interval = trigger_interval
        self._running = False
        self._threads: list[threading.Thread] = []

    def start(self):
        self._running = True
        t1 = threading.Thread(target=self._random_triggers, daemon=True)
        t1.start()
        self._threads.append(t1)
        t2 = threading.Thread(target=self._keyboard_input, daemon=True)
        t2.start()
        self._threads.append(t2)
        logger.info(f"Simulator started — random triggers every ~{self.trigger_interval}s, press 'a'/'b' + Enter for buttons")

    def stop(self):
        self._running = False

    def _random_triggers(self):
        sensor_names = []
        if self.sensors.pir:
            sensor_names.append(("pir", self.sensors.pir))
        if self.sensors.light:
            sensor_names.append(("light", self.sensors.light))
        if self.sensors.sound:
            sensor_names.append(("sound", self.sensors.sound))

        while self._running:
            time.sleep(self.trigger_interval + random.uniform(-3, 3))
            if not self._running or not sensor_names:
                break
            name, sensor = random.choice(sensor_names)
            logger.info(f"[SIM] Triggering sensor: {name}")
            sensor.pin.drive_high()
            time.sleep(0.2)
            sensor.pin.drive_low()

    def _keyboard_input(self):
        """Read 'a' and 'b' keypresses from stdin to simulate button presses."""
        while self._running:
            try:
                if select.select([sys.stdin], [], [], 0.5)[0]:
                    key = sys.stdin.readline().strip().lower()
                    if key == "a" and self.sensors.button_a.when_pressed:
                        logger.info("[SIM] Button A pressed")
                        self.sensors.button_a.pin.drive_low()
                        time.sleep(0.05)
                        self.sensors.button_a.pin.drive_high()
                    elif key == "b" and self.sensors.button_b.when_pressed:
                        logger.info("[SIM] Button B pressed")
                        self.sensors.button_b.pin.drive_low()
                        time.sleep(0.05)
                        self.sensors.button_b.pin.drive_high()
            except (EOFError, OSError):
                break
