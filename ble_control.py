# BLE manual override via the Nordic UART Service (NUS).
#
# Decodes Adafruit Bluefruit Connect "Controller -> Control Pad" packets and
# forwards button-press events to a user-supplied async handler.

import asyncio

import aioble
import bluetooth

import config

# Standard Nordic UART Service UUIDs. Bluefruit Connect speaks to these.
_UART_SERVICE = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_RX = bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E")  # phone -> ESP (write)
_UART_TX = bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E")  # ESP -> phone (notify)

_ADV_INTERVAL_US = 250_000

# Bluefruit Control Pad button packet: '!' 'B' <button> <state> <crc> = 5 bytes.
_PKT_LEN = 5


class BLEControl:
    def __init__(self, on_button):
        # on_button: async callable(button_char: str, pressed: bool)
        self._on_button = on_button
        # Set the GAP device name (0x2A00) before registering services so apps
        # that read it (e.g. Adafruit Bluefruit Connect) show our name rather
        # than MicroPython's default "MPY ESP32".
        _ble = bluetooth.BLE()
        _ble.active(True)
        try:
            _ble.config(gap_name=config.BLE_NAME)
        except Exception as exc:
            print("could not set gap_name:", exc)
        self._service = aioble.Service(_UART_SERVICE)
        self._rx = aioble.Characteristic(
            self._service, _UART_RX, write=True, capture=True
        )
        self._tx = aioble.Characteristic(
            self._service, _UART_TX, notify=True
        )
        aioble.register_services(self._service)
        self._buf = bytearray()

    def notify(self, connection, text):
        # Best-effort status line back to the app's UART console.
        try:
            self._tx.notify(connection, text.encode())
        except Exception:
            pass

    def _extract_packets(self):
        # Pull complete Bluefruit packets out of the rolling buffer.
        # NOTE: MicroPython's bytearray has no slice deletion (`del buf[:n]`),
        # so we advance the buffer with slice assignment instead.
        packets = []
        buf = self._buf
        while True:
            start = buf.find(b"!")
            if start < 0:
                buf[:] = b""
                break
            if start > 0:
                buf[:] = buf[start:]
            if len(buf) < 2:
                break
            # Only the Button command ('B') is fixed-length here; drop anything else.
            if buf[1:2] != b"B":
                buf[:] = buf[1:]
                continue
            if len(buf) < _PKT_LEN:
                break
            packets.append(bytes(buf[:_PKT_LEN]))
            buf[:] = buf[_PKT_LEN:]
        return packets

    async def _handle_writes(self, connection):
        while connection.is_connected():
            try:
                # The RX characteristic is created with capture=True, so the
                # written bytes arrive as the *return value* of written();
                # read() would give an empty value and drop every packet.
                _, data = await self._rx.written()
            except aioble.DeviceDisconnectedError:
                return
            if not data:
                continue
            self._buf.extend(data)
            for pkt in self._extract_packets():
                button = chr(pkt[2])
                pressed = pkt[3] == ord("1")
                await self._on_button(button, pressed)

    async def run(self):
        # Advertise forever; handle one central connection at a time.
        while True:
            try:
                # Name + service UUID alone hit exactly the 31-byte legacy
                # advertising limit; adding appearance pushed it over, which
                # made the ESP32-C3 fall back to extended advertising that
                # iOS/Bluefruit Connect can see but can't actually connect to.
                async with await aioble.advertise(
                    _ADV_INTERVAL_US,
                    name=config.BLE_NAME,
                    services=[_UART_SERVICE],
                ) as connection:
                    print("BLE connected:", connection.device)
                    self._buf[:] = b""
                    await self._handle_writes(connection)
                    print("BLE disconnected")
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                print("BLE error, restarting advertise:", exc)
                await asyncio.sleep_ms(500)
        
