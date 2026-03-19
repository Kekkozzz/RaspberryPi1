import pytest
from sentinelpi.sensors import SensorManager


@pytest.fixture
def sensor_mgr():
    pins = {"pir": 17, "light": 27, "sound": 22, "button_a": 16, "button_b": 26}
    sensor_config = {"pir_enabled": True, "light_enabled": True, "sound_enabled": True}
    mgr = SensorManager(pins, sensor_config)
    yield mgr
    mgr.cleanup()


def test_sensor_manager_creates_sensors(sensor_mgr):
    assert sensor_mgr.pir is not None
    assert sensor_mgr.light is not None
    assert sensor_mgr.sound is not None


def test_sensor_manager_creates_buttons(sensor_mgr):
    assert sensor_mgr.button_a is not None
    assert sensor_mgr.button_b is not None


def test_disabled_sensor_is_none():
    pins = {"pir": 17, "light": 27, "sound": 22, "button_a": 16, "button_b": 26}
    sensor_config = {"pir_enabled": False, "light_enabled": True, "sound_enabled": False}
    mgr = SensorManager(pins, sensor_config)
    assert mgr.pir is None
    assert mgr.light is not None
    assert mgr.sound is None
    mgr.cleanup()


def test_check_sensors_returns_none_when_no_trigger(sensor_mgr):
    triggered = sensor_mgr.check_sensors()
    assert triggered is None


def test_check_sensors_detects_pir(sensor_mgr):
    # Simulate PIR going HIGH
    sensor_mgr.pir.pin.drive_high()
    triggered = sensor_mgr.check_sensors()
    assert triggered == "pir"


def test_check_sensors_skips_disabled():
    pins = {"pir": 17, "light": 27, "sound": 22, "button_a": 16, "button_b": 26}
    sensor_config = {"pir_enabled": False, "light_enabled": True, "sound_enabled": True}
    mgr = SensorManager(pins, sensor_config)
    triggered = mgr.check_sensors()
    assert triggered is None
    mgr.cleanup()
