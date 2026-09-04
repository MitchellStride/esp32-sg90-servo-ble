# ESP32-C3 Squirrel Servo + Retro OLED Terminal

Drives an SG90 servo from an ESP32-C3 Super Mini:

- **Autonomous:** moves to a random angle once per hour.
- **Manual override:** the free **Adafruit Bluefruit Connect** iOS app (Controller -> Control Pad) sends button presses over Bluetooth LE to set presets, jog, or trigger a sweep. Great for live demos, no WiFi needed.
- **Optional retro OLED:** rotates through animated engineer/hacker screens without blocking the servo or Bluetooth tasks.

## Demo

![Demo of the servo sweeping and responding to BLE control](demo.gif)


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

### Optional SSD1306 OLED wiring

| OLED pin | Connects to |
|----------|-------------|
| GND | GND |
| VCC | 3.3V |
| SCL | GPIO9 |
| SDA | GPIO8 |

The tested 0.96-inch 128x64 display uses I2C address `0x3C`. Its top 16 rows
are physically yellow and the remaining rows are blue. Set `OLED_ENABLED =
False` in `config.py` to run the shared codebase without the screen. A missing
screen is also handled gracefully: servo movement and Bluefruit continue.

### OLED modes

The yellow band names the current mode and the blue area animates the content:

1. Bash-style AI terminal with Matrix, Skynut, and squirrel-nut logs
2. Rotating point-cloud Death Star
3. Scrolling voltage oscilloscope
4. Wasteland terminal password hack
5. Falling Matrix-style characters
6. Acorn backup / NUT RAID progress
7. Rotating nut radar
8. Hex packet sniffer

`OLED_MODE_DURATION_S` is set to 30 seconds for testing. Change it to `300`
for five-minute modes. `OLED_MODES` controls which modes run and their order;
`OLED_FRAME_MS` controls animation speed.

## Configuration

The main hardware and behavior settings are collected in `config.py`:

| Setting | Default | Purpose |
|---------|---------|---------|
| `BLE_NAME` | `SQL_Engi` | GAP and advertising name shown in Bluefruit Connect |
| `SERVO_PIN` | `4` | SG90 signal GPIO |
| `MOVE_INTERVAL_S` | `3600` | Seconds between autonomous random head movements |
| `FIRST_MOVE_S` | `30` | Delay before the first autonomous movement after boot |
| `OLED_ENABLED` | `True` | Enables the optional OLED package and animation task |
| `OLED_MODE_DURATION_S` | `30` | Seconds each display mode remains active |
| `OLED_FRAME_MS` | `150` | Delay between animation frames |
| `OLED_MODES` | eight modes | Enabled modes and their rotation order |

Set `OLED_ENABLED = False` to use the same firmware without a display. The
servo and BLE tasks also continue if OLED initialization fails at runtime.

## Files

| File | Purpose |
|------|---------|
| [`boot.py`](boot.py)            | Runs first; disables WiFi (BLE-only) to save power and RAM |
| [`config.py`](config.py)        | Pin, pulse-width limits, angle range, hourly interval, presets, BLE name |
| [`servo.py`](servo.py)          | `Servo` class: `set_angle()`, `jog()`, async `sweep()` and `move_to()` (gradual travel) via 50 Hz PWM |
| [`ble_control.py`](ble_control.py) | Nordic UART Service over `aioble`; decodes Bluefruit Control Pad packets |
| [`main.py`](main.py)            | asyncio loop: hourly random move + BLE override; maps buttons to actions |
| [`oled/controller.py`](oled/controller.py) | Detects the display and rotates modes asynchronously |
| [`oled/modes.py`](oled/modes.py) | Retro terminal and animation renderers |
| [`oled/ssd1306.py`](oled/ssd1306.py) | Included OLED driver; no extra device package needed |

## Flash MicroPython and deploy (over USB)

From your PC (the board appears as a USB serial port; on Windows check Device Manager for the COM port):

1. Install the host tools:

```bash
pip install esptool mpremote
```

2. Download the **ESP32-C3** MicroPython firmware `.bin` from <https://micropython.org/download/ESP32_GENERIC_C3/>. Use the standard (USB) build so the REPL is available over the native USB port.

3. Erase and flash. Hold the BOOT button while plugging in if the board does
   not enter download mode automatically. On Windows, run these as
   `python -m esptool` if the `esptool` command is not on `PATH`.

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
mpremote fs cp -r oled :
```

If `mpremote` is installed as a Python module instead of a command:

```bash
python3 -m mpremote fs cp boot.py config.py servo.py ble_control.py main.py :
python3 -m mpremote fs cp -r oled :
```

6. Reset and watch the logs:

```bash
mpremote reset
mpremote repl
```

You should see the normal servo/BLE startup line, `OLED found at 0x3C; display
modes enabled.`, and an `OLED mode -> ...` line whenever the screen changes.
The autonomous servo still moves after the configured first delay and then at
its regular hourly interval.

`main.py` runs automatically on every boot.

## iOS app setup (Adafruit Bluefruit Connect)

1. Install **Bluefruit Connect** (free) from the App Store.
2. Open the app, enable Bluetooth, and tap **Connect** next to the device named
   by `BLE_NAME` in `config.py` (currently **SQL_Engi**).
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

Mobile operating systems may cache an older BLE name. If the previous name is
still displayed after reflashing, force-close Bluefruit Connect, toggle phone
Bluetooth, or forget the device before scanning again.

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
- Adjust `AUTO_MOVE_STEP_MS` to control how slowly the hourly random move travels (delay in ms per degree of travel; higher = slower).
- Adjust `PRESETS`, `JOG_STEP`, and `REST_ANGLE` to taste.
