import json
import queue
import pytest

from sentinelpi.web.app import create_app


@pytest.fixture
def app():
    cmd_queue = queue.Queue()
    app = create_app(cmd_queue)
    app.config["TESTING"] = True
    return app, cmd_queue


@pytest.fixture
def client(app):
    flask_app, _ = app
    return flask_app.test_client()


def test_index_returns_html(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SentinelPi" in response.data


def test_api_state_returns_json(client):
    response = client.get("/api/state")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "state" in data


def test_api_arm_enqueues_command(app):
    flask_app, cmd_queue = app
    client = flask_app.test_client()
    response = client.post("/api/arm")
    assert response.status_code == 200
    cmd = cmd_queue.get_nowait()
    assert cmd["action"] == "arm"


def test_api_disarm_enqueues_command(app):
    flask_app, cmd_queue = app
    client = flask_app.test_client()
    response = client.post("/api/disarm")
    assert response.status_code == 200
    cmd = cmd_queue.get_nowait()
    assert cmd["action"] == "disarm"


def test_api_reset_enqueues_command(app):
    flask_app, cmd_queue = app
    client = flask_app.test_client()
    response = client.post("/api/reset")
    assert response.status_code == 200
    cmd = cmd_queue.get_nowait()
    assert cmd["action"] == "reset"


def test_api_events_returns_list(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
