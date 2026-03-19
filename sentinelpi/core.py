import queue
import time
import logging

logger = logging.getLogger("sentinelpi.core")


class SentinelCore:
    STATES = ("IDLE", "ARMED", "ALERT", "CHALLENGE", "DISARMED", "ALARM")

    def __init__(self, config: dict, cmd_queue: queue.Queue):
        self.config = config
        self.cmd_queue = cmd_queue
        self.state = "IDLE"
        self.alert_start_time: float = 0
        self.challenge_start_time: float = 0
        self.disarmed_start_time: float = 0
        self._state_listeners: list = []

    def add_state_listener(self, callback):
        """Register a callback(old_state, new_state, extra_info) for state changes."""
        self._state_listeners.append(callback)

    def _set_state(self, new_state: str, **extra):
        old_state = self.state
        self.state = new_state
        logger.info(f"State: {old_state} -> {new_state}")
        for listener in self._state_listeners:
            listener(old_state, new_state, extra)

    def process_commands(self):
        """Drain the command queue and process each command."""
        while not self.cmd_queue.empty():
            try:
                cmd = self.cmd_queue.get_nowait()
            except queue.Empty:
                break
            action = cmd.get("action")
            if action == "arm" and self.state == "IDLE":
                self._set_state("ARMED")
            elif action == "disarm" and self.state == "ARMED":
                self._set_state("IDLE")
            elif action == "reset" and self.state == "ALARM":
                self._set_state("IDLE")

    def on_sensor_triggered(self, sensor_name: str):
        """Called when a sensor detects something while ARMED."""
        if self.state != "ARMED":
            return
        self.alert_start_time = time.monotonic()
        self._set_state("ALERT", sensor=sensor_name)

    def on_challenge_solved(self):
        """Called when the active puzzle is solved."""
        if self.state != "CHALLENGE":
            return
        self.disarmed_start_time = time.monotonic()
        self._set_state("DISARMED")

    def tick(self):
        """Called each main loop iteration to handle timed transitions."""
        now = time.monotonic()

        if self.state == "ALERT":
            elapsed = now - self.alert_start_time
            if elapsed >= self.config["timing"]["alert_grace_seconds"]:
                self.challenge_start_time = now
                self._set_state("CHALLENGE")

        elif self.state == "CHALLENGE":
            elapsed = now - self.challenge_start_time
            if elapsed >= self.config["timing"]["challenge_timeout_seconds"]:
                self._set_state("ALARM")

        elif self.state == "DISARMED":
            elapsed = now - self.disarmed_start_time
            if elapsed >= self.config["timing"]["disarmed_display_seconds"]:
                self._set_state("ARMED")

    def cleanup(self):
        pass
