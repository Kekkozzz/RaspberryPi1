import queue
import json

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO

# Module-level references set by create_app
_cmd_queue: queue.Queue = None
_state_ref: dict = None
_db_ref = None
_config_ref: dict = None
socketio = SocketIO()


def create_app(cmd_queue: queue.Queue, state_ref: dict = None, db=None, config: dict = None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "sentinelpi-dev"

    global _cmd_queue, _state_ref, _db_ref, _config_ref
    _cmd_queue = cmd_queue
    _state_ref = state_ref or {"state": "IDLE", "sensors": {}}
    _db_ref = db
    _config_ref = config

    socketio.init_app(app, async_mode="threading")

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/state")
    def get_state():
        return jsonify(_state_ref)

    @app.route("/api/arm", methods=["POST"])
    def arm():
        _cmd_queue.put({"action": "arm"})
        return jsonify({"ok": True})

    @app.route("/api/disarm", methods=["POST"])
    def disarm():
        _cmd_queue.put({"action": "disarm"})
        return jsonify({"ok": True})

    @app.route("/api/reset", methods=["POST"])
    def reset():
        _cmd_queue.put({"action": "reset"})
        return jsonify({"ok": True})

    @app.route("/api/events")
    def get_events():
        if _db_ref:
            return jsonify(_db_ref.get_recent_events(limit=50))
        return jsonify([])

    @app.route("/api/config", methods=["GET"])
    def get_config():
        return jsonify(_config_ref or {})

    @app.route("/api/config", methods=["POST"])
    def update_config():
        updates = request.get_json()
        if updates and _config_ref:
            for section, values in updates.items():
                if section in _config_ref and isinstance(values, dict):
                    _config_ref[section].update(values)
            _cmd_queue.put({"action": "config_update", "config": _config_ref})
        return jsonify({"ok": True})

    return app


def emit_state_update(state_data: dict):
    """Emit state update to all connected WebSocket clients."""
    socketio.emit("state_update", state_data)


def emit_event(event_data: dict):
    """Emit a new event to all connected WebSocket clients."""
    socketio.emit("new_event", event_data)
