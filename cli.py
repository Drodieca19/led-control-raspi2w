"""
RPi Zero 2W LED Controller - Command Line Interface (CLI)

This is the main entry point of the application. It parses CLI arguments and
invokes the appropriate methods on the LEDController.

Resources Used:
- 'argparse' module: A standard library module used to parse command-line options,
  arguments, and subcommands.
- 'sys' module: Used for system-level controls, such as exiting the process with
  an error code ('sys.exit()').
- 'config' module: Our custom module ('config.py') containing configuration path resolvers.
- 'led.controller' module: Our custom module containing the 'LEDController' class.
"""

import argparse
import sys

# Import our custom modules
import config
from led.controller import LEDController


def main() -> None:
    """
    Main entry function to configure, parse CLI arguments, and control the LED.
    """
    # Create the top-level parser
    # 'argparse.ArgumentParser' handles help messaging and input validation automatically.
    parser = argparse.ArgumentParser(
        description="Educational CLI tool to control the onboard Raspberry Pi Zero 2W LED under DietPi."
    )

    # Resolve default path from config
    default_path: str = config.get_led_base_path()

    # Add a global argument to override the sysfs directory path if needed
    parser.add_argument(
        "--path",
        default=default_path,
        help=f"Override the sysfs path to the LED directory. (Default: {default_path})",
    )

    # Subparsers allow us to define commands (e.g. 'on', 'off', 'blink') instead of flags
    subparsers = parser.add_subparsers(dest="command", required=True, help="Command to run")

    # Command: on
    subparsers.add_parser("on", help="Turn the integrated LED ON")

    # Command: off
    subparsers.add_parser("off", help="Turn the integrated LED OFF")

    # Command: status
    subparsers.add_parser("status", help="Read and display current LED brightness and active trigger")

    # Command: trigger
    trigger_parser = subparsers.add_parser("trigger", help="Set the operating system LED trigger mode")
    trigger_parser.add_argument(
        "name",
        type=str,
        help="Trigger mode name (e.g. 'none', 'heartbeat', 'mmc0', 'default-on')",
    )

    # Command: blink
    blink_parser = subparsers.add_parser("blink", help="Blink the LED at a regular interval")
    blink_parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Pause interval between state changes in seconds (Default: 0.5)",
    )
    blink_parser.add_argument(
        "--count",
        type=int,
        default=5,
        help="Number of times to flash the LED (Default: 5)",
    )

    # Parse command line inputs
    args = parser.parse_args()

    # Instantiate the LED controller with the selected path
    controller = LEDController(args.path)

    # Attempt to verify permissions and execute commands
    try:
        # Check if the process can access hardware sysfs folders
        controller.check_permissions()

        # Route the parsed command to the matching controller action
        if args.command == "on":
            controller.turn_on()
            print("LED has been turned ON.")

        elif args.command == "off":
            controller.turn_off()
            print("LED has been turned OFF.")

        elif args.command == "status":
            brightness = controller.read_status()
            trigger = controller.get_trigger()
            state_text = "ON" if brightness > 0 else "OFF"
            print(f"LED State: {state_text} (brightness value: {brightness})")
            print(f"Active OS Trigger: {trigger}")

        elif args.command == "trigger":
            controller.set_trigger(args.name)
            print(f"LED trigger set to: '{args.name}'")

        elif args.command == "blink":
            print(f"Blinking LED {args.count} times (delay: {args.delay}s)... Press Ctrl+C to cancel.")
            controller.blink(args.delay, args.count)
            print("Blinking complete.")

    except PermissionError as err:
        # Print the descriptive permission tip and exit with error code 1 (Standard error code)
        print(f"Permission Error: {err}", file=sys.stderr)
        sys.exit(1)

    except FileNotFoundError as err:
        # Handle cases where path is missing or incorrect
        print(f"File Error: {err}", file=sys.stderr)
        sys.exit(1)

    except KeyboardInterrupt:
        # Catch Ctrl+C cleanly
        print("\nOperation interrupted by user. Cleaned up.")
        sys.exit(0)


# Standard Python check to ensure this function executes only when run as a script
if __name__ == "__main__":
    main()
