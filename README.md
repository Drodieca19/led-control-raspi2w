# Raspberry Pi Zero 2W LED Controller

An educational Python project to programmatically control the onboard activity (ACT) LED of a Raspberry Pi Zero 2W running DietPi (or other Debian-based operating systems) via standard Linux `sysfs` driver nodes, featuring both a CLI utility and a modern Flask-based Web Dashboard.

---

## Key Features

- **Direct Hardware Control:** Interfaces with system trigger and brightness file nodes without requiring compile-heavy GPIO libraries.
- **Micro Web Interface:** Includes a responsive web GUI built with Flask to control your Pi Zero 2W remotely from any device.
- **Zero Heavy External Dependencies:** The core hardware control uses only Python's standard library. The web interface is built using standard lightweight Flask.
- **Safety Features:** Automatically backs up and restores original hardware trigger settings during execution and handles system interruptions (Ctrl+C) gracefully.
- **Educational Annotations:** Code is written to be beginner-friendly with detailed inline notes explaining how built-in modules, context managers, and exception systems work.
- **Hierarchical Documentation:** Features a structured architecture breakdown (global and module-specific diagrams).

---

## Project Structure

```text
rpi-led-controller/
├── config.py                 # Resolves LED directory paths from env/arguments
├── cli.py                    # Entry point mapping shell commands using argparse
├── app.py                    # Flask Web Server API entry point
├── requirements.txt          # Python dependencies list
├── architecture.md           # Global system design and data-flow diagrams
│
├── led/
│   ├── __init__.py
│   └── controller.py         # Interfaces with /sys/class/leds/ACT control files
│
├── templates/
│   └── index.html            # Web GUI dashboard template (HTML/CSS/JS)
│
└── tests/
    ├── __init__.py
    ├── test_controller.py    # Mock tests for the hardware controller
    └── test_app.py           # Mock tests validating Flask web routing endpoints
```

---

## Installation & Setup

1. **Clone or copy the files** to your Raspberry Pi.
2. Ensure you have **Python 3.12+** installed:
   ```bash
   python --version
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Since modifying kernel `sysfs` files requires root permissions, you must run commands with **sudo**.

---

## Usage Guide (Command Line)

The CLI exposes five subcommands: `on`, `off`, `status`, `trigger`, and `blink`.

### 1. Check Status
Displays whether the LED is active and shows the current kernel trigger name:
```bash
sudo python cli.py status
```

### 2. Manual On/Off
```bash
sudo python python cli.py on
sudo python python cli.py off
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

## Web GUI Dashboard (Flask Server)

You can launch a lightweight, premium web dashboard to control the LED remotely from any web browser on your network using the automated helper script:

### 1. Run the Startup Script
The project includes a `start.sh` script that automatically creates a virtual environment, installs requirements, and runs the server with root privileges:
```bash
# Make the script executable
chmod +x start.sh

# Run the startup automation
./start.sh
```
*(Note: If the script fails during environment creation, you may need to install the venv packages: `sudo apt update && sudo apt install -y python3-venv`)*

### 2. Open in Browser
Open your browser and navigate to:
```text
http://<your-raspberry-pi-ip>:8000
```
Example: `http://192.168.1.15:8000` or `http://dietpi.local:8000`

### 3. Features of the Web Interface
- **Real-time Status Sync:** The dashboard automatically updates every 4 seconds (important if system triggers like `heartbeat` or disk activity are writing to the LED).
- **Graceful Error Alerts:** If you run the web server without root/sudo privileges, the interface stays responsive and displays a visual warning banner instructing how to execute it with `sudo`.
- **Fully Responsive Design:** The interface works beautifully on both desktop and mobile screens.

---

## Running Unit Tests
Tests simulate sysfs file reads, writes, permissions, and delays to run safely on any computer (no Raspberry Pi required):
```bash
# Run all tests
python -m unittest discover -s tests -p "test_*.py"
```

---

## Architectural Details
This codebase follows a strict separation of concerns. You can explore the architectural designs here:
- **System Call Design:** [architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/architecture.md)
- **Controller Module Architecture:** [led/controller.py.architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/led/controller.py.architecture.md)
- **CLI Interface Architecture:** [cli.py.architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/cli.py.architecture.md)
- **Web App Server Architecture:** [app.py.architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/app.py.architecture.md)
- **Web App Tests Architecture:** [tests/test_app.py.architecture.md](file:///c:/Proyectos/Axel/ProyectoSkillsCursoIA/tests/test_app.py.architecture.md)
