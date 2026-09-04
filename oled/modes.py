"""Animated retro-computer modes for the squirrel's two-color OLED."""

import math


class ModeRenderer:
    def __init__(self, oled):
        self.oled = oled
        self._terminal_lines = []
        self._terminal_index = 0
        self._terminal_char = 0
        self._sphere_points = []
        for latitude in range(-75, 76, 25):
            lat = math.radians(latitude)
            for longitude in range(0, 360, 30):
                lon = math.radians(longitude)
                self._sphere_points.append(
                    (math.cos(lat) * math.cos(lon),
                     math.sin(lat),
                     math.cos(lat) * math.sin(lon))
                )

    def start(self, mode_name):
        if mode_name == "broadcom_terminal":
            self._terminal_lines = []
            self._terminal_index = 0
            self._terminal_char = 0

    def draw(self, mode_name, frame):
        if mode_name == "broadcom_terminal":
            self._draw_broadcom_terminal(frame)
        elif mode_name == "death_star":
            self._draw_death_star(frame)
        elif mode_name == "oscilloscope":
            self._draw_oscilloscope(frame)
        elif mode_name == "wasteland_hack":
            self._draw_wasteland_hack(frame)
        elif mode_name == "matrix":
            self._draw_matrix(frame)
        elif mode_name == "nut_backup":
            self._draw_nut_backup(frame)
        elif mode_name == "nut_radar":
            self._draw_nut_radar(frame)
        elif mode_name == "packet_sniffer":
            self._draw_packet_sniffer(frame)
        else:
            self._header("UNKNOWN MODE")
            self.oled.text(mode_name[:16], 0, 32)

    def _header(self, title):
        # Rows 0-15 are the physical yellow band on the two-color panel.
        self.oled.fill(0)
        self.oled.text(title[:16], 0, 4)
        self.oled.hline(0, 15, 128, 1)

    def _draw_broadcom_terminal(self, frame):
        messages = (
            "$ ./skynut.sh",
            "XPU 0xA51C READY",
            "OPENAI LINK UP",
            "ANTHROPIC SYNC",
            "MATRIX: KNOCK",
            "BACKUP 64 NUTS",
            "SAM.ALT> PATCH",
            "DARIO.A> ALIGN",
            "SKYNET -> SKYNUT",
            "AI CACHE: ACORNS",
        )
        current = messages[self._terminal_index]
        if frame % 2 == 0:
            self._terminal_char += 1
            if self._terminal_char > len(current) + 4:
                self._terminal_lines.append(current)
                self._terminal_lines = self._terminal_lines[-4:]
                self._terminal_index = (self._terminal_index + 1) % len(messages)
                self._terminal_char = 0
                current = messages[self._terminal_index]

        self._header("BROADCOM // XPU")
        for row, line in enumerate(self._terminal_lines[-4:]):
            self.oled.text(line[:16], 0, 16 + row * 8)
        typed = current[:min(self._terminal_char, len(current))]
        cursor = "_" if (frame // 3) % 2 == 0 else " "
        self.oled.text((typed + cursor)[:16], 0, 48)
        spinner = "|/-\\"[(frame // 2) % 4]
        self.oled.text("RUN [{}] 0x{:02X}".format(spinner, frame & 0xFF), 0, 56)

    def _draw_death_star(self, frame):
        self._header("DEATH STAR 3D")
        angle = frame * 0.09
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        for x, y, z in self._sphere_points:
            rx = x * cos_a + z * sin_a
            rz = -x * sin_a + z * cos_a
            scale = 19 + 2 * rz
            px = 64 + int(rx * scale)
            py = 39 + int(y * scale)
            if 16 < py < 62:
                self.oled.pixel(px, py, 1)
        # Equatorial trench and the superlaser dish sell the silhouette.
        self.oled.hline(44, 39, 41, 1)
        for degree in range(0, 360, 30):
            rad = math.radians(degree)
            self.oled.pixel(73 + int(5 * math.cos(rad)),
                            30 + int(4 * math.sin(rad)), 1)
        self.oled.text("DS-1 XPU ONLINE", 0, 55)

    def _draw_oscilloscope(self, frame):
        millivolts = 3300 + int(75 * math.sin(frame * 0.13))
        self._header("SCOPE {:d}.{:02d}V".format(
            millivolts // 1000, (millivolts % 1000) // 10))
        for x in range(0, 128, 16):
            for y in range(18, 57, 8):
                self.oled.pixel(x, y, 1)
        previous_x = 0
        previous_y = 38
        phase = frame * 0.22
        for x in range(0, 128, 2):
            y = 38 + int(12 * math.sin(x * 0.105 + phase))
            self.oled.line(previous_x, previous_y, x, y, 1)
            previous_x = x
            previous_y = y
        self.oled.text("CH1 1V  2ms XPU", 0, 56)

    def _draw_wasteland_hack(self, frame):
        self._header("WASTELAND HACK")
        phase = (frame // 22) % 5
        attempts = max(0, 4 - phase)
        self.oled.text("VAULT TERM 7.1", 0, 18)
        self.oled.text("ATTEMPTS LEFT:{}".format(attempts), 0, 26)
        junk = ("{A9F2} NUTS", "[DEAD] C0DE", "<XPU?> 44AC", "{RAD} 03.6")
        self.oled.text(junk[phase % len(junk)], 0, 34)
        guesses = (">ACORNS", ">SQUIRREL", ">SKYNUT", ">BROADCOM", ">ENGINEER")
        self.oled.text(guesses[phase], 0, 42)
        result = "ACCESS GRANTED" if phase == 4 else "ENTRY DENIED"
        self.oled.text(result, 0, 50)
        if (frame // 3) % 2 == 0:
            self.oled.text("_", 0, 58)

    def _draw_matrix(self, frame):
        self._header("MATRIX // LIVE")
        alphabet = "01ABCDEF{}[]$#"
        for column in range(16):
            speed = 1 + column % 3
            head = ((frame // speed) + column * 3) % 7
            for tail in range(3):
                row = (head - tail) % 7
                y = 18 + row * 7
                if y < 57:
                    index = (frame + column * 5 + tail * 7) % len(alphabet)
                    self.oled.text(alphabet[index], column * 8, y)
        self.oled.text("WAKE UP,SQUIRREL", 0, 56)

    def _draw_nut_backup(self, frame):
        self._header("NUT RAID ARRAY")
        percent = (frame * 2) % 101
        self.oled.text("BACKUP: ACORNS", 0, 18)
        self.oled.rect(4, 29, 120, 11, 1)
        width = int(116 * percent / 100)
        if width:
            self.oled.rect(6, 31, width, 7, 1, True)
        self.oled.text("{:3d}%  0x{:04X}".format(percent, frame * 73 & 0xFFFF),
                       0, 43)
        self.oled.text("CACHE: 64 NUTS", 0, 52)

    def _circle(self, cx, cy, radius):
        for degree in range(0, 360, 8):
            rad = math.radians(degree)
            self.oled.pixel(cx + int(radius * math.cos(rad)),
                            cy + int(radius * math.sin(rad)), 1)

    def _draw_nut_radar(self, frame):
        self._header("NUT RADAR")
        cx = 63
        cy = 40
        self._circle(cx, cy, 21)
        self._circle(cx, cy, 13)
        self._circle(cx, cy, 5)
        angle = frame * 0.12
        self.oled.line(cx, cy,
                       cx + int(20 * math.cos(angle)),
                       cy + int(20 * math.sin(angle)), 1)
        blips = ((48, 30), (76, 47), (69, 25))
        visible = 0
        for index, (x, y) in enumerate(blips):
            if (frame // 5 + index) % 3:
                self.oled.rect(x - 1, y - 1, 3, 3, 1, True)
                visible += 1
        self.oled.text("ACORNS:{:02d}".format(visible), 0, 55)

    def _draw_packet_sniffer(self, frame):
        self._header("PACKET SNIFFER")
        value = (frame * 0x45D9 + 0xBEEF) & 0xFFFF
        self.oled.text("RX {:04X} {:04X}".format(value, value ^ 0xA51C), 0, 16)
        self.oled.text("SRC BRCM-XPU", 0, 24)
        self.oled.text("TLS NUT/1.0", 0, 32)
        self.oled.text("ACK {:08X}".format(frame * 7919 & 0xFFFFFFFF), 0, 40)
        self.oled.text("PORT 0x{:04X}".format(0xC000 + frame % 0x3FFF), 0, 48)
        dots = "." * ((frame // 3) % 4)
        self.oled.text(("SNIFFING" + dots)[:16], 0, 56)
