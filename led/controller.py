"""
RPi Zero 2W LED Controller - Core Controller Module

This module implements the LEDController class, which interfaces directly with
the Linux sysfs filesystem to control the integrated LED of a Raspberry Pi Zero 2W.

Resources Used:
- 'os' module: To verify write permissions on the hardware file paths.
- 'time' module: Used for 'time.sleep()' to create delays during the blink cycle.
- 'signal' module / Exception Handling: 'try...finally' block is used to guarantee
  system hardware triggers are restored even if the script is interrupted (Ctrl+C).
"""

import os
import time


class LEDController:
    """
    Controller class to manage the onboard Raspberry Pi LED via Linux sysfs files.
    """

    def __init__(self, base_path: str):
        """
        Initializes the controller with the target sysfs path.

        Note for beginners:
        - We derive the paths to the 'brightness' and 'trigger' files by combining
          the base path with the standard sysfs filenames.
        - 'os.path.join()' is the recommended way to concatenate paths because it
          automatically handles directory separator characters (like '/' or '\')
          correctly depending on the operating system.

        Args:
            base_path (str): Path to the LED sysfs folder (e.g. '/sys/class/leds/ACT').
        """
        self.base_path = base_path
        self.brightness_path = os.path.join(base_path, "brightness")
        self.trigger_path = os.path.join(base_path, "trigger")

    def check_permissions(self) -> None:
        """
        Verifies that the script has the necessary permissions to read and write to the
        LED sysfs control files.

        Note for beginners:
        - 'os.access(path, os.W_OK)' checks if the current process has write access to 'path'.
        - On DietPi/Linux, hardware drivers mapped under '/sys' require root/administrator
          privileges to be modified.
        - If write permission is missing, we raise a custom PermissionError.

        Raises:
            FileNotFoundError: If the sysfs LED directory or control files do not exist.
            PermissionError: If the script is run without sudo (administrator) permissions.
        """
        # First, ensure the control files exist
        if not os.path.exists(self.brightness_path) or not os.path.exists(self.trigger_path):
            raise FileNotFoundError(
                f"LED sysfs control files not found at: {self.base_path}\n"
                "Please verify that this script is running on a Raspberry Pi "
                "with the correct LED configuration path."
            )

        # Check if the files are writable by the current process
        is_brightness_writable = os.access(self.brightness_path, os.W_OK)
        is_trigger_writable = os.access(self.trigger_path, os.W_OK)

        if not is_brightness_writable or not is_trigger_writable:
            # Raise an informative, educational error message
            raise PermissionError(
                "Write permissions denied for the LED control files.\n"
                "To control the integrated hardware LED, you must run this script with root privileges.\n"
                "Try running the command with 'sudo':\n"
                "    sudo python cli.py <command>"
            )

    def turn_on(self) -> None:
        """
        Turns the physical LED on.

        Note for beginners:
        - Writing '1' (or any value greater than 0 up to max_brightness) to the
          'brightness' file turns the LED on.
        - The 'with open(...) as file:' statement is a context manager. It guarantees
          that the file is closed properly as soon as the block exits, even if an error occurs.
        """
        with open(self.brightness_path, "w") as file:
            file.write("1")

    def turn_off(self) -> None:
        """
        Turns the physical LED off.

        Note for beginners:
        - Writing '0' to the 'brightness' file turns the LED off.
        """
        with open(self.brightness_path, "w") as file:
            file.write("0")

    def read_status(self) -> int:
        """
        Reads and returns the current brightness of the LED.

        Note for beginners:
        - '.read()' reads the file contents as a string.
        - '.strip()' removes any whitespace or newline characters ('\n') from the ends.
        - 'int(...)' converts the cleaned string into an integer.

        Returns:
            int: The brightness value (typically 0 for OFF, and 1 or greater for ON).
        """
        with open(self.brightness_path, "r") as file:
            content = file.read().strip()
            return int(content)

    def get_trigger(self) -> str:
        """
        Reads and returns the active system trigger for the LED.

        Note for beginners:
        - The trigger file contains a list of available triggers separated by spaces.
        - The currently active trigger is highlighted inside brackets, e.g.:
          'none [heartbeat] mmc0 default-on'
        - We split the list into words and look for the one starting with '[' and ending with ']'.

        Returns:
            str: The active trigger name (e.g. 'heartbeat', 'none', 'mmc0').
        """
        with open(self.trigger_path, "r") as file:
            content = file.read().strip()

        # Split the string by whitespace into a list of individual triggers
        triggers = content.split()

        for trigger in triggers:
            # Check if this trigger is the active one (enclosed in brackets)
            if trigger.startswith("[") and trigger.endswith("]"):
                # Return the trigger name without the brackets
                return trigger[1:-1]

        return "none"

    def set_trigger(self, trigger_name: str) -> None:
        """
        Sets a new system trigger for the LED.

        Note for beginners:
        - Writing a valid trigger name (like 'heartbeat' or 'none') directly to the
          'trigger' file changes how the operating system handles the LED.

        Args:
            trigger_name (str): The name of the trigger mode to set.
        """
        with open(self.trigger_path, "w") as file:
            file.write(trigger_name)

    def blink(self, interval: float, count: int) -> None:
        """
        Flashes the LED a specified number of times with a delay interval.

        To guarantee manual control over the LED's brightness, the controller
        temporarily sets the trigger to 'none' and restores the original trigger
        upon completion or interruption.

        Note for beginners:
        - 'try...finally' is an exception-handling structure. The code in the 'finally'
          block is GUARANTEED to execute, whether the 'try' code runs successfully,
          crashes with an exception, or is aborted by the user pressing Ctrl+C.
          This is critical for hardware operations to ensure the device is restored to a safe state.

        Args:
            interval (float): Delay time in seconds between state toggles.
            count (int): The number of flash cycles (on + off).
        """
        # Save the current trigger so we can restore it later
        original_trigger = self.get_trigger()

        # Disable automated OS triggers so we can manually adjust brightness
        self.set_trigger("none")

        try:
            for _ in range(count):
                self.turn_on()
                time.sleep(interval)  # Wait with LED ON
                self.turn_off()
                time.sleep(interval)  # Wait with LED OFF
        finally:
            # Restore the original system trigger (e.g. heartbeat or mmc0)
            self.set_trigger(original_trigger)
