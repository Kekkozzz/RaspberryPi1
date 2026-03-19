import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description="SentinelPi security system")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Run in simulation mode without real GPIO hardware",
    )
    args = parser.parse_args()

    if args.simulate:
        import os
        os.environ["GPIOZERO_PIN_FACTORY"] = "mock"

    print(f"SentinelPi v0.1.0 — {'SIMULATION' if args.simulate else 'HARDWARE'} mode")


if __name__ == "__main__":
    main()
