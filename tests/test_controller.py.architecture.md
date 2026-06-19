# Local Architecture: tests/test_controller.py

This document describes the structure and test coverage for the unit test module.

---

## 1. Call Hierarchy

The test module utilizes the `unittest` framework. It patches system access endpoints (like `os` checks and file actions) to isolate testing.

```mermaid
graph TD
    TestRunner([Python Unit Test Runner]) -->|Runs| TestSuite[TestLEDController]
    
    subgraph Test Suite Methods
        TestSuite --> test_default[test_config_default_path]
        TestSuite --> test_env[test_config_env_override]
        TestSuite --> test_perm_ok[test_check_permissions_success]
        TestSuite --> test_perm_fnf[test_check_permissions_file_not_found]
        TestSuite --> test_perm_denied[test_check_permissions_denied]
        TestSuite --> test_on[test_turn_on]
        TestSuite --> test_off[test_turn_off]
        TestSuite --> test_read[test_read_status]
        TestSuite --> test_get_trig[test_get_trigger]
        TestSuite --> test_set_trig[test_set_trigger]
        TestSuite --> test_blink[test_blink]
    end
    
    test_default -->|Checks| config[config.get_led_base_path]
    test_env -->|Checks| config
    test_perm_ok -->|Patches os.access/exists & tests| check[LEDController.check_permissions]
    test_on -->|Mocks open() & tests| on[LEDController.turn_on]
    test_blink -->|Patches sleeps & tests| blink[LEDController.blink]
```

---

## 2. Inputs & Outputs

### `TestLEDController` Class
- **Inputs:** None (Orchestrated by Python `unittest` framework runner).
- **Outputs:** Console output reporting test success or failure codes.
- **Side Effects:** Mocks system level functions using `unittest.mock.patch` to prevent real system writes.

---

## 3. Design Choices & Rationale
- **Filesystem and OS Mocking:**
  Since hardware pathways under `/sys/class/leds/` do not exist on non-Raspberry Pi machines, and require root permission anyway, we patch `os.access`, `os.path.exists`, and built-in `open`. This allows safe, permissionless, and cross-platform verification of code logic.
- **Time Sleep Mocking during Blinking:**
  `LEDController.blink()` loops with `time.sleep()`. In order to keep test executions instantaneous, we mock/patch `time.sleep`. This verifies that the method invokes state changes and sleeps the expected number of times without having the tests block the cpu thread.
