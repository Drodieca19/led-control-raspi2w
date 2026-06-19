# Technical Plan: Raspberry Pi Zero 2W LED Controller

This document details the technical implementation plan (the HOW) for the Python LED controller utility.

---

## Technical Stack & Versions
- **Language:** Python 3.12+
- **Web Framework:** Flask 3.0+ (Micro web framework for routing and web server control).
- **Libraries Used:**
  - `flask`: For web serving and routing.
  - `argparse`: For parsing command-line interfaces.
  - `os`: For checking root permissions and file path access.
  - `sys`: For system-level interactions and status exits.
  - `time`: For interval delays during blinking.
  - `signal`: For capturing Ctrl+C (SIGINT) to ensure graceful restoration of LED states.

---

## Folder Architecture
```text
rpi-led-controller/
│
├── config.py                 # Handles environment variable loading and path configuration
├── cli.py                    # Entry point; parses arguments and invokes the controller
├── app.py                    # Flask server entry point mapping HTTP requests to controller
│
├── led/
│   ├── __init__.py           # Makes led a package
│   └── controller.py         # Interfaces with sysfs file paths to set/get LED properties
│
├── templates/
│   └── index.html            # HTML/CSS/JS dashboard served by Flask
│
└── tests/
    ├── __init__.py
    ├── test_controller.py    # Unit tests mocking file I/O operations
    └── test_app.py           # Unit tests validating Flask routes and JSON outputs
```

---

## Contracts & Interfaces

### `config.py`
```python
def get_led_base_path() -> str:
    """
    Returns the target path to the sysfs LED directory.
    Priority: CLI Override Argument > Environment Variable 'LED_SYSFS_PATH' > Default '/sys/class/leds/ACT'
    """
```

### `led/controller.py`
```python
class LEDController:
    def __init__(self, base_path: str):
        """Initializes controller with base path to the sysfs files."""
        ...

    def check_permissions(self) -> None:
        """
        Checks if the script has write permission to the trigger and brightness files.
        Raises PermissionError with an educational instruction if not run under sudo.
        """
        ...

    def turn_on(self) -> None:
        """Writes '1' to the brightness file."""
        ...

    def turn_off(self) -> None:
        """Writes '0' to the brightness file."""
        ...

    def read_status(self) -> int:
        """Reads and returns the value from the brightness file."""
        ...

    def set_trigger(self, trigger_name: str) -> None:
        """Writes the trigger name (e.g., 'none', 'heartbeat') to the trigger file."""
        ...

    def get_trigger(self) -> str:
        """Reads and returns the active trigger from the trigger file."""
        ...

    def blink(self, interval: float, count: int) -> None:
        """
        Temporarily sets trigger to 'none', blinks the LED 'count' times 
        with 'interval' sleep intervals, and cleans up on completion or interrupt.
        """
        ...
```

### `app.py` (Flask Web Interface)
- **`GET /`**: Renders `templates/index.html` (the web GUI dashboard).
- **`GET /api/led/status`**: Returns JSON `{"status": "ON"|"OFF", "brightness": int, "trigger": str}`.
- **`POST /api/led/on`**: Turns LED on. Returns JSON `{"success": true, "message": "LED turned ON"}`.
- **`POST /api/led/off`**: Turns LED off. Returns JSON `{"success": true, "message": "LED turned OFF"}`.
- **`POST /api/led/trigger`**: Receives JSON body `{"name": "trigger_name"}`. Sets trigger mode. Returns JSON status.
- **`POST /api/led/blink`**: Receives JSON body `{"delay": float, "count": int}`. Initiates a blinking cycle in a background thread or synchronously (synchronous is acceptable for simple API). Returns JSON status.

---

## Execution Sequence
```mermaid
sequenceDiagram
    participant User
    participant Browser as Web Browser (JS fetch)
    participant App as app.py (Flask)
    participant Controller as led/controller.py
    participant Sysfs as OS /sys/class/leds/

    User->>Browser: Click "Turn ON" Button
    Browser->>App: POST /api/led/on
    App->>Controller: turn_on()
    Controller->>Sysfs: Write "1" to brightness
    App-->>Browser: JSON {"success": true}
    Browser-->>User: Update toggle status color
```

---

## Technical Decisions & Rationale

1. **Lightweight Flask Server:**
   - *Decision:* Introduce Flask as the micro web framework for the GUI instead of heavy options like Django or FastAPI (which has heavier type checking / pydantic requirements).
   - *Rationale:* Flask is simple, relies on standard Python structures, is widely used for single-page applications on IoT devices, and serves as an excellent, clear entry point to backend web development for beginners.
2. **Single-Page Application (HTML/JS/CSS Fetch API):**
   - *Decision:* Serve a single HTML page with embedded styling (CSS) and native Javascript (`fetch`).
   - *Rationale:* By using standard browser features (`fetch()`), we avoid the need for heavy Node.js tools, bundlers (Webpack, Vite), or Javascript frameworks (React, Vue). A beginner can inspect the code and see exactly how HTML, CSS, and JS interact directly with Python.
3. **sysfs File Interface:**
   - *Decision:* Read/write to `/sys/class/leds/ACT/brightness` and `/sys/class/leds/ACT/trigger` directly as files.
   - *Rationale:* Under DietPi/Debian Linux, the kernel exposes hardware LEDs as virtual files. Writing "1" or "0" directly is standard practice, works out-of-the-box, and teaches basic file I/O, which is highly educational.
4. **Signal Interrupt Handling:**
   - *Decision:* Use `signal` or `try...finally` block inside the controller/CLI execution.
   - *Rationale:* If the user presses `Ctrl+C` while the LED is blinking, the LED could get stuck in an ON/OFF state or remain with the `none` trigger. A cleanup block ensures the LED is returned to its default system trigger (e.g., `mmc0`).


---
