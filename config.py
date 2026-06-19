"""
RPi Zero 2W LED Controller - Configuration Module

This module is responsible for loading and determining the path configuration
needed to interface with the Raspberry Pi's LED sysfs files.

Resources Used:
- 'os' module: A built-in Python library that provides functions for interacting with
  the operating system. Specifically, we use 'os.environ.get()' to read configuration
  from environment variables.
"""

import os


def get_led_base_path() -> str:
    """
    Retrieves the base filesystem path to the sysfs LED control directory.

    This function implements a configuration hierarchy:
    1. Checks for the environment variable 'LED_SYSFS_PATH'.
    2. Defaults to the standard path '/sys/class/leds/ACT' if the environment
       variable is not set.

    Note for beginners:
    - 'os.environ' is a dictionary-like object containing all active system environment variables.
    - '.get("KEY", default_value)' is a safe dictionary method. If "KEY" exists, it returns its value;
      otherwise, it returns 'default_value' without raising a KeyError exception.

    Returns:
        str: The absolute path to the target LED directory.
    """
    # Define the standard default path for the activity LED on Raspberry Pi Zero 2W
    default_path: str = "/sys/class/leds/ACT"

    # Fetch the environment variable 'LED_SYSFS_PATH' if set by the user,
    # otherwise fallback to the default path.
    resolved_path: str = os.environ.get("LED_SYSFS_PATH", default_path)

    return resolved_path
