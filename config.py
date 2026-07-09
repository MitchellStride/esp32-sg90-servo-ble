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

# Name advertised over BLE; this is what you tap to connect in Bluefruit Connect.
BLE_NAME = "rat"
