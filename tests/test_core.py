import queue
import pytest

from sentinelpi.core import SentinelCore
from sentinelpi.config import DEFAULT_CONFIG


@pytest.fixture
def core():
    cmd_queue = queue.Queue()
    c = SentinelCore(DEFAULT_CONFIG, cmd_queue)
    yield c
    c.cleanup()


def test_initial_state_is_idle(core):
    assert core.state == "IDLE"


def test_arm_command(core):
    core.cmd_queue.put({"action": "arm"})
    core.process_commands()
    assert core.state == "ARMED"


def test_disarm_from_armed(core):
    core.cmd_queue.put({"action": "arm"})
    core.process_commands()
    core.cmd_queue.put({"action": "disarm"})
    core.process_commands()
    assert core.state == "IDLE"


def test_disarm_ignored_in_idle(core):
    core.cmd_queue.put({"action": "disarm"})
    core.process_commands()
    assert core.state == "IDLE"


def test_sensor_trigger_in_armed(core):
    core.state = "ARMED"
    core.on_sensor_triggered("pir")
    assert core.state == "ALERT"


def test_sensor_trigger_ignored_in_idle(core):
    core.state = "IDLE"
    core.on_sensor_triggered("pir")
    assert core.state == "IDLE"


def test_alert_to_challenge_after_grace(core):
    core.state = "ALERT"
    core.alert_start_time = 0  # long ago
    core.tick()
    assert core.state == "CHALLENGE"


def test_challenge_timeout_to_alarm(core):
    core.state = "CHALLENGE"
    core.challenge_start_time = 0  # long ago
    core.tick()
    assert core.state == "ALARM"


def test_challenge_solved(core):
    core.state = "CHALLENGE"
    core.on_challenge_solved()
    assert core.state == "DISARMED"


def test_disarmed_rearms_after_delay(core):
    core.state = "DISARMED"
    core.disarmed_start_time = 0  # long ago
    core.tick()
    assert core.state == "ARMED"


def test_reset_from_alarm(core):
    core.state = "ALARM"
    core.cmd_queue.put({"action": "reset"})
    core.process_commands()
    assert core.state == "IDLE"


def test_reset_ignored_outside_alarm(core):
    core.state = "ARMED"
    core.cmd_queue.put({"action": "reset"})
    core.process_commands()
    assert core.state == "ARMED"
