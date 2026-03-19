import json
import copy

DEFAULT_CONFIG = {
    "pins": {
        "pir": 17,
        "light": 27,
        "sound": 22,
        "led_red": 5,
        "led_green": 6,
        "led_blue": 13,
        "buzzer": 19,
        "button_a": 16,
        "button_b": 26,
    },
    "timing": {
        "alert_grace_seconds": 3,
        "challenge_timeout_seconds": 15,
        "alarm_auto_reset_seconds": 0,
        "disarmed_display_seconds": 3,
    },
    "difficulty": {
        "difficulty_level": 1,
        "max_sequence_length": 8,
        "button_rhythm_tolerance_ms": 200,
    },
    "sensors": {
        "pir_enabled": True,
        "light_enabled": True,
        "sound_enabled": True,
    },
    "web": {
        "host": "0.0.0.0",
        "port": 5000,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Merge override into base, filling missing keys from base."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def load_config(path: str) -> dict:
    """Load config from JSON file, falling back to defaults for missing keys."""
    try:
        with open(path) as f:
            user_config = json.load(f)
        return _deep_merge(DEFAULT_CONFIG, user_config)
    except FileNotFoundError:
        return copy.deepcopy(DEFAULT_CONFIG)


def save_config(path: str, config: dict) -> None:
    """Save config dict to JSON file."""
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def difficulty_to_sequence_length(level: int) -> int:
    """Convert difficulty level (1-5) to base sequence length (3-7)."""
    clamped = max(1, min(5, level))
    return clamped + 2
