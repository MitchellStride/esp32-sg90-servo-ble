# Runs once at power-on, before main.py.
#
# This project talks over Bluetooth LE only, so WiFi is switched off to save
# power and free RAM. Remove this file if you later add WiFi features.

import network


def _disable_wifi():
    for iface_id in (network.STA_IF, network.AP_IF):
        try:
            iface = network.WLAN(iface_id)
            if iface.active():
                iface.active(False)
        except Exception as exc:
            print("boot: could not disable WiFi iface", iface_id, exc)


_disable_wifi()
print("boot: WiFi disabled (BLE-only mode)")
