import random
import time


class SimonSaysChallenge:
    """LED sequence memory puzzle. User cycles colors with Button A, confirms with Button B."""
    name = "simon"

    def __init__(self, sequence_length: int):
        colors = ("red", "green", "blue")
        self.sequence = [random.choice(colors) for _ in range(sequence_length)]
        self.position = 0
        self.current_color = "red"

    def cycle_color(self):
        """Button A pressed — cycle to next color."""
        colors = ("red", "green", "blue")
        idx = colors.index(self.current_color)
        self.current_color = colors[(idx + 1) % 3]
        return self.current_color

    def submit_selection(self) -> str:
        """Button B pressed — confirm current color selection.
        Returns: 'next' (correct, more to go), 'solved' (all correct), 'wrong' (restart)."""
        if self.current_color == self.sequence[self.position]:
            self.position += 1
            if self.position >= len(self.sequence):
                return "solved"
            return "next"
        else:
            self.position = 0
            return "wrong"


class CountingChallenge:
    """Count the beeps puzzle. Press Button A to count, Button B to confirm."""
    name = "counting"

    def __init__(self, sequence_length: int):
        self.target = random.randint(3, max(3, sequence_length))
        self.press_count = 0

    def press_a(self):
        """Button A pressed — increment count."""
        self.press_count += 1

    def submit_count(self) -> str:
        """Button B pressed — check if count matches target.
        Returns: 'solved' or 'wrong'."""
        if self.press_count == self.target:
            return "solved"
        self.press_count = 0
        return "wrong"


class ButtonRhythmChallenge:
    """Rhythm replication puzzle. Listen to pattern, replicate timing with Button A."""
    name = "rhythm"

    def __init__(self, sequence_length: int, tolerance_ms: int = 200):
        self.tolerance_ms = tolerance_ms
        self.pattern = [random.choice([300, 500, 800]) for _ in range(sequence_length - 1)]
        self.recording: list[float] = []
        self._last_press_time: float | None = None

    def press_a(self):
        """Button A pressed — record timestamp."""
        now = time.monotonic()
        if self._last_press_time is not None:
            interval_ms = (now - self._last_press_time) * 1000
            self.recording.append(interval_ms)
        self._last_press_time = now

    def check_rhythm(self) -> str:
        """Check if recorded rhythm matches pattern.
        Returns: 'solved' or 'wrong'."""
        if len(self.recording) != len(self.pattern):
            self.recording = []
            self._last_press_time = None
            return "wrong"
        for recorded, expected in zip(self.recording, self.pattern):
            if abs(recorded - expected) > self.tolerance_ms:
                self.recording = []
                self._last_press_time = None
                return "wrong"
        return "solved"


def pick_challenge(sequence_length: int, tolerance_ms: int = 200):
    """Randomly pick one of the available challenges."""
    choice = random.choice(["simon", "counting", "rhythm"])
    if choice == "simon":
        return SimonSaysChallenge(sequence_length)
    elif choice == "counting":
        return CountingChallenge(sequence_length)
    else:
        return ButtonRhythmChallenge(sequence_length, tolerance_ms)
