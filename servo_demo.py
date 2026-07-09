# Standalone servo demo: steps through a set of angles every 10 seconds.
#
# No BLE, no hourly timer -- just visible, repeating motion so you can confirm
# the servo and wiring work while the BLE hardware issue is sorted out.
#
# Run it over USB without installing it as main.py:
#     mpremote connect COM3 run servo_demo.py
# ...or copy it to the board and import it from the REPL:
#     mpremote fs cp servo_demo.py :
#     mpremote exec "import servo_demo"

import time

from servo import Servo
import config

# Angles to visit, in order, looping forever.
_SEQUENCE = (0, 45, 90, 135, 180, 135, 90, 45)
_INTERVAL_S = 10


def run():
    servo = Servo()
    print("servo demo: stepping every {}s. Ctrl-C to stop.".format(_INTERVAL_S))
    i = 0
    while True:
        angle = _SEQUENCE[i % len(_SEQUENCE)]
        servo.set_angle(angle)
        print("-> {} deg".format(angle))
        i += 1
        time.sleep(_INTERVAL_S)


run()
