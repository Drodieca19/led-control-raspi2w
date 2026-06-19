# Tasks Checklist: RPi Zero 2W LED Controller

This document lists the atomic, ordered, and traceable tasks required to implement the LED controller project.

---

## Task Checklist

### [x] T-01: Project Setup & Configuration Loading
- **Description:** Initialize project file structure, configure `.gitignore`, and implement `config.py` to resolve the LED sysfs path.
- **Traceability:** `[RF-06]`, `[RNF-02]`, `[RNF-04]`
- **Acceptance Criteria:**
  - `config.py` correctly resolves the path to `/sys/class/leds/ACT` by default.
  - Path can be overridden via `LED_SYSFS_PATH` environment variable.
- **Dependencies:** None.

### [x] T-02: LED Controller Core & Permission Verification
- **Description:** Implement `LEDController.__init__` and `check_permissions` in `led/controller.py`.
- **Traceability:** `[RNF-03]`, `[RNF-04]`
- **Acceptance Criteria:**
  - Instantiating `LEDController(base_path)` creates the controller pointing to target files.
  - `check_permissions()` verifies write permissions to sysfs files and raises a helpful, beginner-friendly `PermissionError` explaining how to run with `sudo` if permissions are denied.
- **Dependencies:** T-01.

### [x] T-03: Implement Basic LED Control (On, Off, Status)
- **Description:** Implement `turn_on()`, `turn_off()`, and `read_status()` in `LEDController`.
- **Traceability:** `[RF-01]`, `[RF-02]`, `[RNF-04]`
- **Acceptance Criteria:**
  - `turn_on()` writes `"1"` to `brightness` file.
  - `turn_off()` writes `"0"` to `brightness` file.
  - `read_status()` returns integer value read from `brightness` file.
- **Dependencies:** T-02.

### [x] T-04: Implement Trigger Operations & Safe Blinking Control
- **Description:** Implement `set_trigger()`, `get_trigger()`, and `blink()` in `LEDController` with signal exception safety.
- **Traceability:** `[RF-03]`, `[RF-04]`, `[RNF-05]`
- **Acceptance Criteria:**
  - `get_trigger()` parses active trigger from output list.
  - `set_trigger(name)` writes new trigger mode to `trigger` file.
  - `blink(interval, count)` sets trigger to `"none"`, flashes the LED, and restores the original trigger on finish or SIGINT interrupt.
- **Dependencies:** T-03.

### [x] T-05: Implement Command-Line Interface (CLI)
- **Description:** Implement `cli.py` using Python's standard `argparse` library.
- **Traceability:** `[RF-05]`, `[RNF-04]`
- **Acceptance Criteria:**
  - CLI exposes actions: `on`, `off`, `status`, `trigger`, and `blink`.
  - Accept CLI arguments for base path overrides.
  - Catches `PermissionError` and reports the educational tip to the user.
- **Dependencies:** T-04.

### [x] T-06: Implement Unit Testing Suite
- **Description:** Create tests in `tests/test_controller.py` using Python's built-in `unittest` and `unittest.mock`.
- **Traceability:** `[RNF-04]`
- **Acceptance Criteria:**
  - Tests verify configurations, permission checks, state changes, and blinking sequences by mocking file accesses.
  - Suite passes cleanly when running `python -m unittest tests/test_controller.py`.
- **Dependencies:** T-05.

### [x] T-07: Configure Web GUI Dependencies & HTML Template
- **Description:** Create `requirements.txt` declaring `flask` dependency and implement `templates/index.html` with modern dark glassmorphic styling and JavaScript native `fetch()` connection handlers.
- **Traceability:** `[RF-07]`, `[RNF-07]`
- **Acceptance Criteria:**
  - `requirements.txt` declares `flask>=3.0.0`.
  - `templates/index.html` renders controls for on/off, blink parameters, OS triggers, status indicators, and displays error messages correctly.
- **Dependencies:** T-05.

### [x] T-08: Implement Flask Server Routes & Web Controller API
- **Description:** Implement `app.py` server initializing Flask routing structures, serving index HTML, and translation of API queries (GET/POST status, toggles, trigger changes, blink loops) to the controller.
- **Traceability:** `[RF-08]`, `[RNF-06]`
- **Acceptance Criteria:**
  - Running `python app.py` starts Flask server bound to port 8000.
  - REST endpoints (`/api/led/status`, `/api/led/on`, `/api/led/off`, `/api/led/trigger`, `/api/led/blink`) correctly process requests and return JSON.
  - Missing write permissions (root/sudo) are handled gracefully by returning a `403 Forbidden` JSON error rather than crashing on launch.
- **Dependencies:** T-07.

### [x] T-09: Add Web Routing Unit Tests
- **Description:** Implement Flask test client routes coverage inside `tests/test_app.py`.
- **Traceability:** `[RNF-06]`, `[RNF-04]`
- **Acceptance Criteria:**
  - `tests/test_app.py` passes all unit tests validating GET/POST routes and JSON return payloads.
  - Tests pass cleanly when running `python -m unittest tests/test_app.py`.
- **Dependencies:** T-08.

