# Architecture Design: RPi Zero 2W LED Controller

This document outlines the global hierarchical function and module call structure, data flows, and architectural choices for the Raspberry Pi Zero 2W LED Controller.

---

## 1. System Architecture Diagram

The system is designed with a layered approach separating CLI/Interface handling, Configuration gathering, and Hardware control via file input/output (sysfs).

```mermaid
graph TD
    User([User CLI input]) -->|Runs| CLI[cli.py]
    CLI -->|Imports & calls| Config[config.py]
    CLI -->|Instantiates & executes| Controller[led/controller.py]
    Controller -->|Reads/Writes sysfs| OS[Linux Kernel /sys/class/leds/]
```

---

## 2. Module Call Hierarchy

```mermaid
flowchart TD
    subgraph CLI Entry Point (cli.py)
        A[main] --> B[parse_arguments]
    end
    
    subgraph Configuration (config.py)
        C[get_led_base_path]
    end

    subgraph Core Control (led/controller.py)
        D[LEDController.__init__]
        E[LEDController.check_permissions]
        F[LEDController.turn_on]
        G[LEDController.turn_off]
        H[LEDController.read_status]
        I[LEDController.set_trigger]
        J[LEDController.get_trigger]
        K[LEDController.blink]
    end

    A -->|1. Resolves path| C
    A -->|2. Instantiates| D
    A -->|3. Verifies root| E
    
    A -->|Option: on| F
    A -->|Option: off| G
    A -->|Option: status| H
    A -->|Option: status| J
    A -->|Option: trigger| I
    A -->|Option: blink| K
    
    K -->|Blink loop| F
    K -->|Blink loop| G
    K -->|Backup/Restore| J
    K -->|Backup/Restore| I
```

---

## 3. Data Flows (Inputs & Outputs)

| Step / Function | Input Data | Output Data / Side Effects | Description |
|---|---|---|---|
| `config.get_led_base_path()` | None (Checks CLI arguments, env vars `LED_SYSFS_PATH`) | `str` (Path to sysfs directory) | Resolves directory path to the target LED sysfs interface. |
| `LEDController.__init__(base_path)` | `base_path: str` | Instance variables initialized | Creates the controller pointing to the device paths. |
| `LEDController.check_permissions()` | None | None / Raises `PermissionError` | Checks write accessibility of critical files. |
| `LEDController.turn_on()` | None | Writes `"1"` to `brightness` file | Turns the physical LED on. |
| `LEDController.turn_off()` | None | Writes `"0"` to `brightness` file | Turns the physical LED off. |
| `LEDController.read_status()` | None | `int` (Brightness level, e.g. `0` or `1`) | Reads value from physical `brightness` file. |
| `LEDController.set_trigger(name)` | `trigger_name: str` | Writes trigger to `trigger` file | Alters operating system LED behavior. |
| `LEDController.get_trigger()` | None | `str` (Active trigger mode) | Reads trigger list and identifies active trigger. |
| `LEDController.blink(interval, count)` | `interval: float`, `count: int` | Flashes LED, restores original trigger on finish/interrupt | Blinks physical LED repeatedly. |

---

## 4. Architectural Choices & Rationale

- **Modular Separation of Concerns:**
  By isolating command line arguments (`cli.py`), configuration values (`config.py`), and direct hardware sysfs modifications (`led/controller.py`), we achieve a clean codebase. If the hardware pathway shifts in the future (e.g. from sysfs files to a GPIO library), only `led/controller.py` will require modifications.
- **Zero-Dependency Pipeline:**
  Standard Python libraries are used exclusively. For an educational project, this is highly beneficial: students do not need to manage virtual env toolings (`pip`, `poetry`) just to interact with system files.
- **Resource Protection and Graceful Interruption:**
  Linux sysfs trigger values are temporarily set to `none` during manual brightness writes, as automated system routines (e.g. disk write operations) would otherwise overwrite manual triggers. Restoring these triggers within `try...finally` statements guarantees that hardware defaults are restored even if execution is abruptly terminated.
