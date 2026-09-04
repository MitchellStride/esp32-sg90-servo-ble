# Configuration for the ESP32-C3 SG90 servo controller.

# GPIO pin driving the servo signal (orange) wire.
SERVO_PIN = 4

# Servo PWM pulse-width limits in nanoseconds at 50 Hz (20 ms period).
# 0.5 ms .. 2.5 ms maps to 0 .. 180 degrees. If the SG90 jitters at the
# extremes or fails to reach the ends, narrow these toward 1_000_000 / 2_000_000.
PULSE_MIN_NS = 500_000
PULSE_MAX_NS = 2_500_000

# Mechanical travel limits in degrees.
ANGLE_MIN = 0
ANGLE_MAX = 180

# Position the servo returns to after a sweep and on boot.
REST_ANGLE = 90

# Autonomous move cadence: pick a random angle once per hour.
MOVE_INTERVAL_S = 3600

# Delay before the *first* autonomous move after boot. Kept short so you can
# confirm auto mode works without waiting a full interval; later moves use
# MOVE_INTERVAL_S.
FIRST_MOVE_S = 30

# How slowly the autonomous random move travels: delay in milliseconds
# between each 1-degree step. Higher = slower travel. At 30ms/deg, a full
# 180-degree sweep takes ~5.4s; a typical ~90 degree move takes ~2.7s.
AUTO_MOVE_STEP_MS = 30

# Step size (degrees) for the BLE jog buttons (Up / Down on the Control Pad).
JOG_STEP = 10

# Time to settle at each end of an on-demand sweep, in milliseconds.
SWEEP_DWELL_MS = 600

# Preset angles mapped to Bluefruit Connect Control Pad numbered buttons 1-3.
PRESETS = {
    "1": 0,
    "2": 90,
    "3": 180,
}

# Name used for both the BLE GAP device name and advertising payload; this is
# what you tap to connect in Bluefruit Connect.
BLE_NAME = "SQL_Engi"

# Optional 0.96-inch 128x64 SSD1306 OLED. Set this to False to run the exact
# same servo + Bluefruit behavior without importing or initializing the OLED.
OLED_ENABLED = True
OLED_SDA_PIN = 8
OLED_SCL_PIN = 9
OLED_I2C_FREQ = 400_000
OLED_ADDR = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 64

# Each display mode normally sits for five minutes. This is intentionally set
# to 30 seconds while the animations are being tested; change it to 300 for
# the finished installation.
OLED_MODE_DURATION_S = 30
OLED_FRAME_MS = 150

# Display order. Remove a name to disable that mode or rearrange the tuple to
# change the rotation order.
OLED_MODES = (
    "broadcom_terminal",
    "death_star",
    "oscilloscope",
    "wasteland_hack",
    "matrix",
    "nut_backup",
    "nut_radar",
    "packet_sniffer",
)
