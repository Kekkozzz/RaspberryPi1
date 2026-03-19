import argparse
import logging
import os
import queue
import signal
import sys
import threading
import time

from sentinelpi import __version__
from sentinelpi.config import load_config, difficulty_to_sequence_length
from sentinelpi.database import EventDB
from sentinelpi.core import SentinelCore
from sentinelpi.challenge import pick_challenge
from sentinelpi.web.app import create_app, socketio, emit_state_update, emit_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("sentinelpi")


def main():
    parser = argparse.ArgumentParser(description="SentinelPi security system")
    parser.add_argument("--simulate", action="store_true", help="Run without real GPIO")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    args = parser.parse_args()

    if args.simulate:
        os.environ["GPIOZERO_PIN_FACTORY"] = "mock"

    # Late imports so GPIOZERO_PIN_FACTORY is set before gpiozero loads
    from sentinelpi.actuators import Actuators
    from sentinelpi.sensors import SensorManager

    config = load_config(args.config)
    logger.info(f"SentinelPi v{__version__} — {'SIMULATION' if args.simulate else 'HARDWARE'} mode")

    # Initialize components
    from pathlib import Path
    project_dir = Path(__file__).resolve().parent
    db = EventDB(str(project_dir / "data" / "events.db"))
    cmd_queue = queue.Queue()
    core = SentinelCore(config, cmd_queue)
    actuators = Actuators(config["pins"])
    sensors = SensorManager(config["pins"], config["sensors"])

    # Shared state for web dashboard
    state_ref = {"state": "IDLE", "sensors": {}}

    # State change listener — update actuators, database, web
    active_challenge = [None]  # mutable container for closure

    def on_state_change(old_state, new_state, extra):
        state_ref["state"] = new_state
        actuators.set_state(new_state)
        db.log_event(
            "state_change",
            state_from=old_state,
            state_to=new_state,
            sensor=extra.get("sensor"),
        )
        update_data = dict(state_ref)
        if new_state == "CHALLENGE":
            update_data["challenge_remaining"] = config["timing"]["challenge_timeout_seconds"]
        emit_state_update(update_data)
        emit_event({
            "event_type": "state_change",
            "state_from": old_state,
            "state_to": new_state,
            "sensor": extra.get("sensor"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        })

        # Start challenge when entering CHALLENGE state
        if new_state == "CHALLENGE":
            daily_alarms = db.get_daily_alarm_count()
            base_len = difficulty_to_sequence_length(config["difficulty"]["difficulty_level"])
            seq_len = min(base_len + daily_alarms, config["difficulty"]["max_sequence_length"])
            active_challenge[0] = pick_challenge(
                seq_len, config["difficulty"]["button_rhythm_tolerance_ms"]
            )
            logger.info(f"Challenge started: {active_challenge[0].name} (length={seq_len})")

    core.add_state_listener(on_state_change)

    # Button callbacks
    def on_button_a():
        if core.state == "CHALLENGE" and active_challenge[0]:
            ch = active_challenge[0]
            if hasattr(ch, "press_a"):
                ch.press_a()
            if hasattr(ch, "cycle_color"):
                ch.cycle_color()
        elif core.state in ("IDLE", "ARMED"):
            cmd_queue.put({"action": "arm" if core.state == "IDLE" else "disarm"})

    def on_button_b():
        if core.state == "CHALLENGE" and active_challenge[0]:
            ch = active_challenge[0]
            result = None
            if hasattr(ch, "submit_selection"):
                result = ch.submit_selection()
            elif hasattr(ch, "submit_count"):
                result = ch.submit_count()
            elif hasattr(ch, "check_rhythm"):
                result = ch.check_rhythm()
            if result == "solved":
                core.on_challenge_solved()
        elif core.state == "ALARM":
            cmd_queue.put({"action": "reset"})

    sensors.button_a.when_pressed = on_button_a
    sensors.button_b.when_pressed = on_button_b

    # Web server in background thread
    app = create_app(cmd_queue, state_ref, db, config)
    web_thread = threading.Thread(
        target=lambda: socketio.run(
            app,
            host=config["web"]["host"],
            port=config["web"]["port"],
            allow_unsafe_werkzeug=True,
            use_reloader=False,
        ),
        daemon=True,
    )
    web_thread.start()
    logger.info(f"Dashboard: http://{config['web']['host']}:{config['web']['port']}")

    # Set initial actuator state
    actuators.set_state("IDLE")

    # Start simulator if in simulation mode
    simulator = None
    if args.simulate:
        from sentinelpi.simulator import Simulator
        simulator = Simulator(sensors)
        simulator.start()

    # Graceful shutdown
    running = True

    def shutdown(signum, frame):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Main loop
    try:
        while running:
            core.process_commands()

            # Check sensors only when ARMED
            if core.state == "ARMED":
                triggered = sensors.check_sensors()
                if triggered:
                    core.on_sensor_triggered(triggered)

            core.tick()
            time.sleep(0.05)  # 50ms loop
    finally:
        logger.info("Shutting down...")
        if simulator:
            simulator.stop()
        actuators.cleanup()
        sensors.cleanup()
        db.close()


if __name__ == "__main__":
    main()
