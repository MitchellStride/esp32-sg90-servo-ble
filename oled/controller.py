"""OLED hardware setup and asynchronous display-mode rotation."""

import asyncio
import time
from machine import Pin, SoftI2C

import config
from oled.modes import ModeRenderer
from oled.ssd1306 import SSD1306_I2C


class OLEDController:
    def __init__(self):
        self.i2c = SoftI2C(
            sda=Pin(config.OLED_SDA_PIN),
            scl=Pin(config.OLED_SCL_PIN),
            freq=config.OLED_I2C_FREQ,
        )
        devices = self.i2c.scan()
        if config.OLED_ADDR not in devices:
            found = ", ".join("0x{:02X}".format(address) for address in devices)
            raise OSError(
                "OLED 0x{:02X} not found; I2C scan: {}".format(
                    config.OLED_ADDR, found or "no devices"
                )
            )
        self.oled = SSD1306_I2C(
            config.OLED_WIDTH,
            config.OLED_HEIGHT,
            self.i2c,
            addr=config.OLED_ADDR,
        )
        self.renderer = ModeRenderer(self.oled)

    async def run(self):
        try:
            while True:
                for mode_name in config.OLED_MODES:
                    print("OLED mode ->", mode_name)
                    self.renderer.start(mode_name)
                    started = time.ticks_ms()
                    frame = 0
                    duration_ms = int(config.OLED_MODE_DURATION_S * 1000)
                    while time.ticks_diff(time.ticks_ms(), started) < duration_ms:
                        self.renderer.draw(mode_name, frame)
                        self.oled.show()
                        frame += 1
                        await asyncio.sleep_ms(config.OLED_FRAME_MS)
        except Exception as exc:
            # A display failure should not cancel the servo and BLE coroutines
            # gathered alongside this task.
            print("OLED task stopped; servo/BLE continuing:", exc)
