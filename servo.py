# SG90 servo driver using hardware PWM on the ESP32-C3.

import asyncio
from machine import Pin, PWM

import config


class Servo:
    def __init__(self, pin=config.SERVO_PIN):
        # SG90 expects a 50 Hz signal (20 ms period).
        self._pwm = PWM(Pin(pin), freq=50)
        self._angle = None
        self.set_angle(config.REST_ANGLE)

    @property
    def angle(self):
        return self._angle

    def _angle_to_ns(self, deg):
        span = config.ANGLE_MAX - config.ANGLE_MIN
        frac = (deg - config.ANGLE_MIN) / span
        return int(config.PULSE_MIN_NS + (config.PULSE_MAX_NS - config.PULSE_MIN_NS) * frac)

    def set_angle(self, deg):
        deg = max(config.ANGLE_MIN, min(config.ANGLE_MAX, int(deg)))
        self._pwm.duty_ns(self._angle_to_ns(deg))
        self._angle = deg
        return deg

    def jog(self, delta):
        return self.set_angle(self._angle + delta)

    async def move_to(self, deg, step_delay_ms=config.AUTO_MOVE_STEP_MS):
        # Travel to `deg` one degree at a time instead of snapping, so the
        # move is visibly slower. step_delay_ms controls the speed: bigger
        # number = slower travel. Awaited/stepped like sweep() so BLE stays
        # responsive during the move.
        deg = max(config.ANGLE_MIN, min(config.ANGLE_MAX, int(deg)))
        step = 1 if deg >= self._angle else -1
        for d in range(self._angle, deg + step, step):
            self.set_angle(d)
            await asyncio.sleep_ms(step_delay_ms)
        return self._angle

    async def sweep(self):
        # Travel to both extremes then return to the rest position.
        # Stepped + awaited so the BLE server stays responsive during the move.
        for target in (config.ANGLE_MIN, config.ANGLE_MAX, config.REST_ANGLE):
            step = 1 if target >= self._angle else -1
            for deg in range(self._angle, target + step, step):
                self.set_angle(deg)
                await asyncio.sleep_ms(5)
            await asyncio.sleep_ms(config.SWEEP_DWELL_MS)
        return self._angle
