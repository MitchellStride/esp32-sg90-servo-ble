# Entry point: drives an SG90 on the ESP32-C3.
#
#   * Autonomously moves to a random angle once per hour.
#   * Accepts a manual override from the Adafruit Bluefruit Connect iOS app
#     (Controller -> Control Pad) over Bluetooth LE.

import asyncio
import random

import config
from servo import Servo
from ble_control import BLEControl

# Bluefruit Control Pad button layout: 1-4 numbered, 5=Up 6=Down 7=Left 8=Right.
_BTN_SWEEP = "4"
_BTN_UP = "5"
_BTN_DOWN = "6"

servo = Servo()
# Serialise motion so an hourly move and a manual sweep never fight the PWM.
_motion_lock = asyncio.Lock()


async def _sweep():
    async with _motion_lock:
        print("sweep: start")
        await servo.sweep()
        print("sweep: rest at", servo.angle)


async def on_button(button, pressed):
    # Act only on the press edge; ignore the matching release.
    if not pressed:
        return
    if button in config.PRESETS:
        angle = config.PRESETS[button]
        async with _motion_lock:
            servo.set_angle(angle)
        print("preset {} -> {} deg".format(button, angle))
    elif button == _BTN_SWEEP:
        await _sweep()
    elif button == _BTN_UP:
        async with _motion_lock:
            servo.jog(config.JOG_STEP)
        print("jog up ->", servo.angle)
    elif button == _BTN_DOWN:
        async with _motion_lock:
            servo.jog(-config.JOG_STEP)
        print("jog down ->", servo.angle)


async def hourly_task():
    # First move happens after a short delay so auto mode is visible right away;
    # every move after that waits the full hourly interval.
    delay = config.FIRST_MOVE_S
    while True:
        await asyncio.sleep(delay)
        angle = random.randint(config.ANGLE_MIN, config.ANGLE_MAX)
        async with _motion_lock:
            await servo.move_to(angle)
        print("auto-move ->", angle, "deg")
        delay = config.MOVE_INTERVAL_S


async def main():
    ble = BLEControl(on_button)
    print("Servo at rest ({} deg). Advertising BLE as '{}'.".format(
        servo.angle, config.BLE_NAME))
    await asyncio.gather(hourly_task(), ble.run())


try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()
