import pytest
from unittest.mock import MagicMock

from sentinelpi.challenge import (
    SimonSaysChallenge,
    CountingChallenge,
    ButtonRhythmChallenge,
    pick_challenge,
)


class TestSimonSays:
    def test_generate_sequence_length(self):
        ch = SimonSaysChallenge(sequence_length=4)
        assert len(ch.sequence) == 4

    def test_sequence_uses_valid_colors(self):
        ch = SimonSaysChallenge(sequence_length=5)
        for color in ch.sequence:
            assert color in ("red", "green", "blue")

    def test_correct_input_advances(self):
        ch = SimonSaysChallenge(sequence_length=3)
        ch.sequence = ["red", "green", "blue"]
        ch.current_color = "red"
        result = ch.submit_selection()
        assert result == "next"

    def test_wrong_input_resets(self):
        ch = SimonSaysChallenge(sequence_length=3)
        ch.sequence = ["red", "green", "blue"]
        ch.current_color = "green"  # wrong — should be red
        result = ch.submit_selection()
        assert result == "wrong"

    def test_correct_full_sequence_wins(self):
        ch = SimonSaysChallenge(sequence_length=2)
        ch.sequence = ["red", "green"]
        ch.current_color = "red"
        ch.submit_selection()
        ch.current_color = "green"
        result = ch.submit_selection()
        assert result == "solved"


class TestCounting:
    def test_generate_target(self):
        ch = CountingChallenge(sequence_length=5)
        assert 3 <= ch.target <= 5

    def test_correct_count_wins(self):
        ch = CountingChallenge(sequence_length=5)
        ch.target = 4
        ch.press_count = 4
        result = ch.submit_count()
        assert result == "solved"

    def test_wrong_count_fails(self):
        ch = CountingChallenge(sequence_length=5)
        ch.target = 4
        ch.press_count = 3
        result = ch.submit_count()
        assert result == "wrong"

    def test_increment_press(self):
        ch = CountingChallenge(sequence_length=5)
        ch.press_a()
        ch.press_a()
        assert ch.press_count == 2


class TestPickChallenge:
    def test_pick_returns_valid_challenge(self):
        ch = pick_challenge(sequence_length=3)
        assert ch is not None
        assert hasattr(ch, "name")

    def test_pick_respects_sequence_length(self):
        for _ in range(20):
            ch = pick_challenge(sequence_length=5)
            if isinstance(ch, SimonSaysChallenge):
                assert len(ch.sequence) == 5
            elif isinstance(ch, CountingChallenge):
                assert 3 <= ch.target <= 5
