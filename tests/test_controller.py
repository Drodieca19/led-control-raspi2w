"""
RPi Zero 2W LED Controller - Unit Testing Suite

This module contains unit tests to verify the correctness of the LEDController and
configuration loading modules. It mocks hardware filesystem writes/reads so that
the tests can run safely on any computer without physical hardware access.

Resources Used:
- 'unittest' module: A built-in Python framework for writing and running test cases.
- 'unittest.mock' module: Specifically 'patch' and 'mock_open', which allow us to replace
  real system interactions (like checking if a file exists or writing to a file) with
  fake structures ("mocks"). This isolates the logic we want to test.
"""

import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

# Import the modules we want to test
import config
from led.controller import LEDController


class TestLEDController(unittest.TestCase):
    """
    TestCase class defining tests for config loading and the LEDController methods.
    """

    def setUp(self) -> None:
        """
        Runs before every test case. Sets up a default base path.
        """
        self.base_path = "/sys/class/leds/ACT"
        self.controller = LEDController(self.base_path)

    @patch.dict(os.environ, {}, clear=True)
    def test_config_default_path(self) -> None:
        """
        Verifies that config returns the default path when no env var is present.
        """
        path = config.get_led_base_path()
        self.assertEqual(path, "/sys/class/leds/ACT")

    @patch.dict(os.environ, {"LED_SYSFS_PATH": "/custom/path"}, clear=True)
    def test_config_env_override(self) -> None:
        """
        Verifies that config respects the LED_SYSFS_PATH environment variable.
        """
        path = config.get_led_base_path()
        self.assertEqual(path, "/custom/path")

    @patch("led.controller.os.path.exists")
    @patch("led.controller.os.access")
    def test_check_permissions_success(self, mock_access: MagicMock, mock_exists: MagicMock) -> None:
        """
        Verifies check_permissions passes when files exist and write access is granted.
        """
        # Tell our mocks to return True (simulating successful checks)
        mock_exists.return_value = True
        mock_access.return_value = True

        # Calling this should not raise any exceptions
        try:
            self.controller.check_permissions()
        except Exception as e:
            self.fail(f"check_permissions raised an unexpected exception: {e}")

    @patch("led.controller.os.path.exists")
    def test_check_permissions_file_not_found(self, mock_exists: MagicMock) -> None:
        """
        Verifies check_permissions raises FileNotFoundError if control files do not exist.
        """
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            self.controller.check_permissions()

    @patch("led.controller.os.path.exists")
    @patch("led.controller.os.access")
    def test_check_permissions_denied(self, mock_access: MagicMock, mock_exists: MagicMock) -> None:
        """
        Verifies check_permissions raises PermissionError if files are not writable (no sudo).
        """
        mock_exists.return_value = True
        mock_access.return_value = False  # Simulate read-only access (lack of root)

        with self.assertRaises(PermissionError):
            self.controller.check_permissions()

    def test_turn_on(self) -> None:
        """
        Verifies turn_on writes '1' to the brightness file.
        """
        # Create a mock open tool that records what is written to the file
        m_open = mock_open()
        with patch("builtins.open", m_open):
            self.controller.turn_on()

        # Check that the file was opened for writing at the correct path
        m_open.assert_called_once_with(self.controller.brightness_path, "w")
        # Check that '1' was written to the file
        m_open().write.assert_called_once_with("1")

    def test_turn_off(self) -> None:
        """
        Verifies turn_off writes '0' to the brightness file.
        """
        m_open = mock_open()
        with patch("builtins.open", m_open):
            self.controller.turn_off()

        m_open.assert_called_once_with(self.controller.brightness_path, "w")
        m_open().write.assert_called_once_with("0")

    def test_read_status(self) -> None:
        """
        Verifies read_status reads the brightness file and returns the integer value.
        """
        # Create a mock file containing the string '1\n' (LED is active)
        m_open = mock_open(read_data="1\n")
        with patch("builtins.open", m_open):
            status = self.controller.read_status()

        self.assertEqual(status, 1)
        m_open.assert_called_once_with(self.controller.brightness_path, "r")

    def test_get_trigger(self) -> None:
        """
        Verifies get_trigger parses the active trigger correctly from brackets.
        """
        # Simulates typical kernel sysfs output: bracketed word is active
        mock_data = "none [heartbeat] mmc0 default-on"
        m_open = mock_open(read_data=mock_data)

        with patch("builtins.open", m_open):
            trigger = self.controller.get_trigger()

        self.assertEqual(trigger, "heartbeat")
        m_open.assert_called_once_with(self.controller.trigger_path, "r")

    def test_set_trigger(self) -> None:
        """
        Verifies set_trigger writes the trigger name to the trigger file.
        """
        m_open = mock_open()
        with patch("builtins.open", m_open):
            self.controller.set_trigger("none")

        m_open.assert_called_once_with(self.controller.trigger_path, "w")
        m_open().write.assert_called_once_with("none")

    @patch("led.controller.time.sleep")  # Mock sleep so tests run instantly without delay
    @patch("led.controller.LEDController.get_trigger")
    @patch("led.controller.LEDController.set_trigger")
    @patch("led.controller.LEDController.turn_on")
    @patch("led.controller.LEDController.turn_off")
    def test_blink(
        self,
        mock_off: MagicMock,
        mock_on: MagicMock,
        mock_set_trig: MagicMock,
        mock_get_trig: MagicMock,
        mock_sleep: MagicMock,
    ) -> None:
        """
        Verifies the blinking flow: backs up trigger, disables trigger, blinks, and restores trigger.
        """
        # Configure initial trigger
        mock_get_trig.return_value = "heartbeat"

        # Trigger the blink command
        self.controller.blink(interval=0.1, count=3)

        # Check trigger backup was checked
        mock_get_trig.assert_called_once()

        # Check trigger was disabled and then restored to 'heartbeat' in correct sequence
        # Call 1: disable trigger -> set_trigger("none")
        # Call 2: restore trigger -> set_trigger("heartbeat")
        mock_set_trig.assert_any_call("none")
        mock_set_trig.assert_any_call("heartbeat")
        self.assertEqual(mock_set_trig.call_count, 2)

        # Verify loop executed state changes 3 times each
        self.assertEqual(mock_on.call_count, 3)
        self.assertEqual(mock_off.call_count, 3)
        # 3 ON sleeps and 3 OFF sleeps = 6 total sleeps
        self.assertEqual(mock_sleep.call_count, 6)


if __name__ == "__main__":
    unittest.main()
