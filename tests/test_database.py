import os
import tempfile

import pytest

from sentinelpi.database import EventDB


@pytest.fixture
def db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    database = EventDB(path)
    yield database
    database.close()
    os.unlink(path)


def test_log_event_and_retrieve(db):
    db.log_event("state_change", state_from="IDLE", state_to="ARMED")
    events = db.get_recent_events(limit=10)
    assert len(events) == 1
    assert events[0]["event_type"] == "state_change"
    assert events[0]["state_from"] == "IDLE"
    assert events[0]["state_to"] == "ARMED"


def test_log_sensor_trigger(db):
    db.log_event("sensor_trigger", state_from="ARMED", state_to="ALERT", sensor="pir")
    events = db.get_recent_events(limit=10)
    assert events[0]["sensor"] == "pir"


def test_log_event_with_details(db):
    db.log_event("challenge_result", details='{"puzzle": "simon", "result": "success"}')
    events = db.get_recent_events(limit=10)
    assert "simon" in events[0]["details"]


def test_get_recent_events_respects_limit(db):
    for i in range(20):
        db.log_event("state_change", state_from="IDLE", state_to="ARMED")
    events = db.get_recent_events(limit=5)
    assert len(events) == 5


def test_get_recent_events_newest_first(db):
    db.log_event("state_change", state_from="IDLE", state_to="ARMED")
    db.log_event("state_change", state_from="ARMED", state_to="ALERT")
    events = db.get_recent_events(limit=10)
    assert events[0]["state_to"] == "ALERT"  # newest first


def test_daily_alarm_count(db):
    db.log_event("state_change", state_from="CHALLENGE", state_to="ALARM")
    db.log_event("state_change", state_from="CHALLENGE", state_to="ALARM")
    db.log_event("state_change", state_from="IDLE", state_to="ARMED")  # not an alarm
    count = db.get_daily_alarm_count()
    assert count == 2
