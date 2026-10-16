# CircuitPython / MicroPython USB HID Firmware for Raspberry Pi Pico
#
# Installation Guide:
# 1. Download CircuitPython UF2 for Raspberry Pi Pico from https://circuitpython.org/board/raspberry_pi_pico/
# 2. Hold the BOOTSEL button on your Pico while plugging it into your PC.
# 3. Drag and drop the downloaded .uf2 file onto the RPI-RP2 drive.
# 4. Copy the 'adafruit_hid' folder into the 'lib' folder on the CIRCUITPY drive.
# 5. Copy this script as 'code.py' (or 'main.py') onto the root of the CIRCUITPY drive.

import sys
import time
import usb_hid
from adafruit_hid.mouse import Mouse

mouse = Mouse(usb_hid.devices)

print("Pico HID Mouse Ready")
sys.stdout.flush()

while True:
    try:
        line = sys.stdin.readline().strip()
        if not line:
            continue

        if "PING" in line:
            print("PONG")
            sys.stdout.flush()
        elif line.startswith("M,"):
            parts = line.split(",")
            if len(parts) == 3:
                dx = int(parts[1])
                dy = int(parts[2])
                mouse.move(x=dx, y=dy)
        elif "CLICK" in line or line == "C":
            mouse.click(Mouse.LEFT_BUTTON)
    except Exception as e:
        time.sleep(0.001)
