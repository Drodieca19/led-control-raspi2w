# Specification: Raspberry Pi Zero 2W LED Controller

This document specifies the requirements (the WHAT and the WHY) for a Python project to control the integrated LED of a Raspberry Pi Zero 2W running DietPi as the operating system.

---

## Status
- **Status:** Approved
- **Version:** 1.0.0
- **Author:** @architect
- **Last Updated:** 2026-06-19

---

## Background & Rationale
Raspberry Pi Zero 2W has an onboard LED (normally acting as `ACT` disk activity indicator). When running a minimal OS like DietPi, users often want to control this LED programmatically (e.g., to notify when services are running, flash status updates, or signal errors) without installing heavy external GUI tools or complicated libraries.
This project provides a simple, educational Python utility using standard Linux sysfs operations to control the onboard LED.

---

## Functional Requirements (FR)

- **[RF-01] On/Off Control:** The program must allow turning the integrated LED ON and OFF.
- **[RF-02] Read LED Status:** The program must be able to read and display the current brightness value of the LED.
- **[RF-03] Blinking Mode:** The program must support blinking the LED with a configurable duration (interval in seconds) and a configurable repeat count.
- **[RF-04] Trigger Configuration:** The program must allow setting the LED's trigger mode (e.g., `none` to control manually, `heartbeat` for pulse pattern, or `mmc0` for disk activity).
- **[RF-05] CLI Interface:** The program must provide a Command Line Interface (CLI) using Python's standard library (`argparse`) to invoke all commands (e.g., `on`, `off`, `status`, `blink`, `trigger`).
- **[RF-06] Configuration Customization:** The system must use `/sys/class/leds/ACT` as the default directory path, but support overriding it via environment variables or CLI arguments.

---

## Non-Functional Requirements (RNF)

- **[RNF-01] Platform Target:** Built specifically for DietPi / Debian Linux on Raspberry Pi Zero 2W.
- **[RNF-02] sysfs Interface:** Must interact with the LED via the standard Linux filesystem path `/sys/class/leds/ACT` (or configurable sibling directory).
- **[RNF-03] Root Privilege Safety:** The program must run with root/sudo privileges. It must check for write permissions to the LED file descriptor and raise a clear, beginner-friendly error if root/sudo privileges are missing.
- **[RNF-04] Educational and Beginner-Friendly:** The source code must be simple, readable, and fully documented, explaining Python built-in functions (e.g., file context managers `with`, `sys.argv`, etc.).
- **[RNF-05] Clean Resource Cleanup:** In case of errors or SIGINT (Ctrl+C) during blinking, the program must restore the LED trigger and state to its original values before exiting.

---

## Open Questions (User Review Required)

*(All questions resolved: path is configurable, CLI uses standard library, execution is under sudo privileges.)*

---

## Traceability Matrix
*(Will be populated in `/tasks` phase)*
| RF/RNF ID | Task ID | Description | Status |
|---|---|---|---|
| [RF-01] | T-03 | On/Off Control | Completed |
| [RF-02] | T-03 | Read Status | Completed |
| [RF-03] | T-04 | Blinking Mode | Completed |
| [RF-04] | T-04 | Trigger Control | Completed |
| [RF-05] | T-05 | CLI Interface | Completed |
| [RF-06] | T-01 | Configuration Customization | Completed |
| [RNF-03] | T-02 | Root Privilege Check | Completed |
| [RNF-04] | T-01, T-02, T-03, T-04, T-05, T-06 | Educational Standard | Completed |
| [RNF-05] | T-04 | Graceful Cleanup | Completed |
