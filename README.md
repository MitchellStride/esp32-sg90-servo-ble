# ESP32-C3 SG90 Servo Controller (MicroPython + BLE override)

Drives an SG90 servo from an ESP32-C3 Super Mini:

- **Autonomous:** moves to a random angle once per hour.
- **Manual override:** the free **Adafruit Bluefruit Connect** iOS app (Controller -> Control Pad) sends button presses over Bluetooth LE to set presets, jog, or trigger a sweep. Great for live demos, no WiFi needed.

## Hardware wiring

SG90 has three wires:

| SG90 wire | Connects to |
|-----------|-------------|
| Brown (GND)    | GND (shared ground) |
| Red (V+)       | 5V pin (USB 5V on the Super Mini) |
| Orange (signal)| GPIO4 |

Notes:
- The 3.3V logic signal from GPIO4 is accepted by the SG90.
- One SG90 runs fine off the board's 5V/USB rail. If you add more servos or see brownouts/resets, power the servo from a separate 5V supply and tie the grounds together.
- The signal pin is set in [`config.py`](config.py) (`SERVO_PIN`).

## Files

| File | Purpose |
|------|---------|
| [`boot.py`](boot.py)            | Runs first; disables WiFi (BLE-only) to save power and RAM |
| [`config.py`](config.py)        | Pin, pulse-width limits, angle range, hourly interval, presets, BLE name |
| [`servo.py`](servo.py)          | `Servo` class: `set_angle()`, `jog()`, async `sweep()` via 50 Hz PWM |
| [`ble_control.py`](ble_control.py) | Nordic UART Service over `aioble`; decodes Bluefruit Control Pad packets |
| [`main.py`](main.py)            | asyncio loop: hourly random move + BLE override; maps buttons to actions |

## Flash MicroPython and deploy (over USB)

From your PC (the board appears as a USB serial port; on Windows check Device Manager for the COM port):

1. Install the host tools:

```bash
pip install esptool mpremote
```

2. Download the **ESP32-C3** MicroPython firmware `.bin` from <https://micropython.org/download/ESP32_GENERIC_C3/>. Use the standard (USB) build so the REPL is available over the native USB port.

3. Erase and flash (hold the BOOT button while plugging in if the board doesn't enter download mode automatically):
[python -m] can be added to the front of cmds for win11 cmd

```bash
esptool --chip esp32c3 erase_flash
esptool --chip esp32c3 write_flash 0x0 ESP32_GENERIC_C3-<version>.bin

```

4. Install the BLE helper library onto the board (`bluetooth` is built in; `aioble` is not):

```bash
mpremote mip install aioble
```

5. Copy the project files to the board's filesystem:

```bash
mpremote fs cp boot.py config.py servo.py ble_control.py main.py :
```

6. Reset and watch the logs:

```bash
mpremote reset
mpremote repl
```

You should see `Servo at rest (90 deg). Advertising BLE as 'ESP32C3-Servo'.` and an `hourly auto-move -> N deg` line once per hour.

`main.py` runs automatically on every boot.

## iOS app setup (Adafruit Bluefruit Connect)

1. Install **Bluefruit Connect** (free) from the App Store.
2. Open the app, enable Bluetooth, and tap **Connect** next to the **ESP32C3-Servo** device (name from `config.py` `BLE_NAME`).
3. Choose **Controller**, then **Control Pad**.
4. Use the buttons:

| Button | Action |
|--------|--------|
| 1 | Move to 0 deg |
| 2 | Move to 90 deg |
| 3 | Move to 180 deg |
| 4 | Sweep (0 -> 180 -> rest) |
| Up    | Jog +10 deg |
| Down  | Jog -10 deg |

The hourly auto-move keeps running while connected; manual commands take effect immediately (last command wins).

## Quick bench test

In the REPL, drive the servo directly without waiting for the hourly timer:

```python
from servo import Servo
s = Servo()
s.set_angle(0)
s.set_angle(180)
s.set_angle(90)
```

## Tuning

- If the servo jitters at the extremes or can't quite reach 0/180, narrow `PULSE_MIN_NS` / `PULSE_MAX_NS` in [`config.py`](config.py) toward `1_000_000` / `2_000_000`.
- Change `MOVE_INTERVAL_S` to test the autonomous move faster (e.g. `15` seconds).
- Adjust `PRESETS`, `JOG_STEP`, and `REST_ANGLE` to taste.
