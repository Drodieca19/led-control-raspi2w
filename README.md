# Raspberry Pi Zero 2W LED Controller

An educational, dependency-free Python project to programmatically control the onboard activity (ACT) LED of a Raspberry Pi Zero 2W running DietPi (or other Debian-based operating systems) via standard Linux `sysfs` driver nodes.

---

## Key Features

- **Direct Hardware Control:** Interfaces with system trigger and brightness file nodes without requiring compile-heavy GPIO libraries.
- **Zero External Dependencies:** Built entirely with Python's standard library (`argparse`, `os`, `sys`, `time`, `signal`).
- **Safety Features:** Automatically backs up and restores original hardware trigger settings during execution and handles system interruptions (Ctrl+C) gracefully.
- **Educational Annotations:** Code is written to be beginner-friendly with detailed inline notes explaining how built-in modules, context managers, and exception systems work.
- **Hierarchical Documentation:** Features a structured architecture breakdown (global and module-specific diagrams).

---

## Project Structure

```text
rpi-led-controller/
├── config.py                 # Resolves LED directory paths from env/arguments
├── cli.py                    # Entry point mapping shell commands using argparse
├── architecture.md           # Global system design and data-flow diagrams
│
├── led/
│   ├── __init__.py
│   └── controller.py         # Interfaces with /sys/class/leds/ACT control files
│
└── tests/
    ├── __init__.py
    └── test_controller.py    # Mock tests run safely without physical hardware
```

---

## Installation & Setup

1. **Clone or copy the files** to your Raspberry Pi.
2. Ensure you have **Python 3.12+** installed:
   ```bash
   python --version
   ```
3. Since modifying kernel `sysfs` files requires root permissions, you must run commands with **sudo**.

---

## Usage Guide

The CLI exposes five subcommands: `on`, `off`, `status`, `trigger`, and `blink`.

### 1. Check Status
Displays whether the LED is active and shows the current kernel trigger name:
```bash
sudo python cli.py status
```

### 2. Manual On/Off
```bash
sudo python cli.py on
sudo python cli.py off
```

### 3. Change System Trigger
You can assign kernel triggers to make the LED display heartbeat pulses or disk activity:
```bash
# Pulsing pattern
sudo python cli.py trigger heartbeat

# Back to manual command control
sudo python cli.py trigger none
```

### 4. Blinking Cycle
Blink the LED a set number of times with a custom delay between toggles. This command temporarily disables active triggers and restores them when complete:
```bash
# Blink 10 times, with 0.2 second intervals
sudo python cli.py blink --delay 0.2 --count 10
```

### 5. Overriding LED Directory
If your OS mounts the LED at a different location (e.g. `led0` instead of `ACT`), you can pass the path as a parameter or set an environment variable:
```bash
# Parameter override
sudo python cli.py --path /sys/class/leds/led0 blink

# Environment variable override
export LED_SYSFS_PATH="/sys/class/leds/led0"
sudo -E python cli.py status
```
*(Note: `-E` tells sudo to preserve environment variables like `LED_SYSFS_PATH`)*

---

## Running Unit Tests
Tests simulate sysfs file reads, writes, permissions, and delays to run safely on any computer (no Raspberry Pi required):
```bash
python -m unittest tests/test_controller.py
```

---

## Architectural Details
This codebase follows a strict separation of concerns. You can explore the architectural designs here:
- **System Call Design:** [architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/architecture.md)
- **Controller Module Architecture:** [led/controller.py.architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/led/controller.py.architecture.md)
- **CLI Interface Architecture:** [cli.py.architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/cli.py.architecture.md)
