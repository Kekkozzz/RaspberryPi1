import pytest

from sentinelpi.actuators import Actuators


@pytest.fixture
def actuators():
    pins = {"led_red": 5, "led_green": 6, "led_blue": 13, "buzzer": 19}
    act = Actuators(pins)
    yield act
    act.cleanup()


def test_all_off(actuators):
    actuators.all_off()
    assert actuators.led_red.value == 0
    assert actuators.led_green.value == 0
    assert actuators.led_blue.value == 0
    assert actuators.buzzer.value == 0


def test_set_led(actuators):
    actuators.set_led("red", True)
    assert actuators.led_red.value == 1
    actuators.set_led("red", False)
    assert actuators.led_red.value == 0


def test_set_led_invalid_color(actuators):
    with pytest.raises(ValueError):
        actuators.set_led("purple", True)


def test_buzzer_on_off(actuators):
    actuators.buzzer_on()
    assert actuators.buzzer.value == 1
    actuators.buzzer_off()
    assert actuators.buzzer.value == 0


def test_set_state_idle(actuators):
    actuators.set_state("IDLE")
    # In IDLE, green blinks — we just check no crash and others are off
    assert actuators.led_red.value == 0
    assert actuators.led_blue.value == 0


def test_set_state_armed(actuators):
    actuators.set_state("ARMED")
    assert actuators.led_green.value == 1
    assert actuators.led_red.value == 0
    assert actuators.led_blue.value == 0


def test_set_state_alarm(actuators):
    actuators.set_state("ALARM")
    assert actuators.led_red.value == 1
    assert actuators.buzzer.value == 1
