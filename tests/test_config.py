import json
import os
import tempfile

import pytest

from sentinelpi.config import load_config, DEFAULT_CONFIG


def test_load_config_returns_default_when_file_missing():
    config = load_config("/nonexistent/path/config.json")
    assert config == DEFAULT_CONFIG


def test_load_config_reads_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        custom = {**DEFAULT_CONFIG, "web": {"host": "127.0.0.1", "port": 9999}}
        json.dump(custom, f)
        path = f.name
    try:
        config = load_config(path)
        assert config["web"]["port"] == 9999
    finally:
        os.unlink(path)


def test_load_config_merges_missing_keys():
    """If config file is missing some keys, defaults fill in."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"web": {"host": "127.0.0.1", "port": 9999}}, f)
        path = f.name
    try:
        config = load_config(path)
        assert config["web"]["port"] == 9999
        assert "pins" in config  # filled from defaults
        assert config["pins"]["pir"] == 17
    finally:
        os.unlink(path)


def test_default_config_has_all_required_sections():
    for section in ("pins", "timing", "difficulty", "sensors", "web"):
        assert section in DEFAULT_CONFIG


def test_difficulty_to_sequence_length():
    from sentinelpi.config import difficulty_to_sequence_length
    assert difficulty_to_sequence_length(1) == 3
    assert difficulty_to_sequence_length(5) == 7


def test_difficulty_to_sequence_length_clamped():
    from sentinelpi.config import difficulty_to_sequence_length
    assert difficulty_to_sequence_length(0) == 3  # min clamp
    assert difficulty_to_sequence_length(10) == 7  # max clamp
