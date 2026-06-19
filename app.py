"""
RPi Zero 2W LED Controller - Web Server Application (Flask)

This is the entry point for the Web GUI dashboard. It launches a Flask server
that provides a browser interface and translates HTTP API calls into hardware commands.

Resources Used:
- 'flask' package: An external micro-framework used to construct web routes.
  - 'Flask': The main application class.
  - 'render_template': Renders HTML files located in the 'templates/' folder.
  - 'jsonify': Converts Python dictionaries into JSON format for REST APIs.
  - 'request': Accesses incoming HTTP request data (e.g. POST JSON payloads).
- 'config' module: Resolves target LED folder path.
- 'led.controller' module: Our custom controller interface to the sysfs hardware nodes.
"""

import sys
from flask import Flask, jsonify, render_template, request

# Import custom configurations and controller
import config
from led.controller import LEDController

# Initialize the Flask application instance
app = Flask(__name__)

# Fetch standard configuration path
led_base_path = config.get_led_base_path()
controller = LEDController(led_base_path)

# Verify permissions at startup. We store the error instead of crashing,
# which allows us to serve a helpful warning page in the browser.
permission_error_message = None
try:
    controller.check_permissions()
except (PermissionError, FileNotFoundError) as err:
    permission_error_message = str(err)


@app.route("/")
def index():
    """
    Serves the main Web GUI Dashboard (HTML template).

    Note for beginners:
    - Flask automatically searches for templates inside the 'templates/' folder.
    - If a permission error occurred at startup, we still serve the HTML page,
      and Javascript will handle displaying the warning alert.
    """
    return render_template("index.html")


@app.route("/api/led/status", methods=["GET"])
def get_status():
    """
    API Endpoint: Reads and returns the current state of the LED.

    Returns:
        JSON response with the current brightness state ('ON' or 'OFF') and the active trigger.
    """
    # If the server is running without write permissions, return a JSON error
    if permission_error_message:
        return jsonify({"error": permission_error_message}), 403

    try:
        brightness = controller.read_status()
        active_trigger = controller.get_trigger()
        status_text = "ON" if brightness > 0 else "OFF"

        return jsonify({
            "status": status_text,
            "brightness": brightness,
            "trigger": active_trigger
        })
    except Exception as err:
        return jsonify({"error": f"Failed to read hardware state: {err}"}), 500


@app.route("/api/led/on", methods=["POST"])
def turn_on():
    """
    API Endpoint: Turns the physical LED ON.
    """
    if permission_error_message:
        return jsonify({"error": permission_error_message}), 403

    try:
        controller.turn_on()
        return jsonify({"success": True, "message": "LED turned ON"})
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@app.route("/api/led/off", methods=["POST"])
def turn_off():
    """
    API Endpoint: Turns the physical LED OFF.
    """
    if permission_error_message:
        return jsonify({"error": permission_error_message}), 403

    try:
        controller.turn_off()
        return jsonify({"success": True, "message": "LED turned OFF"})
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@app.route("/api/led/trigger", methods=["POST"])
def set_trigger():
    """
    API Endpoint: Sets the operating system LED trigger mode.
    Expects a JSON body containing {"name": "trigger_name"}.
    """
    if permission_error_message:
        return jsonify({"error": permission_error_message}), 403

    # Parse incoming JSON data safely
    data = request.get_json(silent=True)
    if not data or "name" not in data:
        return jsonify({"error": "Invalid payload. Expected JSON: {'name': 'trigger_name'}"}), 400

    trigger_name = data["name"]

    try:
        controller.set_trigger(trigger_name)
        return jsonify({"success": True, "message": f"Trigger changed to {trigger_name}"})
    except Exception as err:
        return jsonify({"error": str(err)}), 500


@app.route("/api/led/blink", methods=["POST"])
def trigger_blink():
    """
    API Endpoint: Toggles the LED ON and OFF dynamically.
    Expects a JSON body containing {"delay": float, "count": int}.
    """
    if permission_error_message:
        return jsonify({"error": permission_error_message}), 403

    data = request.get_json(silent=True)
    if not data or "delay" not in data or "count" not in data:
        return jsonify({"error": "Invalid payload. Expected JSON: {'delay': float, 'count': int}"}), 400

    try:
        delay = float(data["delay"])
        count = int(data["count"])
        
        # Execute blink (synchronous block: Flask will pause client requests until loop completes)
        controller.blink(delay, count)
        
        return jsonify({"success": True, "message": f"Successfully blinked {count} times"})
    except ValueError:
        return jsonify({"error": "Delay and count must be valid numbers."}), 400
    except Exception as err:
        return jsonify({"error": str(err)}), 500


# Runs the web application if this file is executed directly
if __name__ == "__main__":
    # Serve locally on port 8000. 'host="0.0.0.0"' makes the server accessible 
    # from other devices in the same network (crucial for remote control of the Pi)
    app.run(host="0.0.0.0", port=8000, debug=False)
