#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import serial
import threading
import time
import termios
import tty

# === Configuration ===
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200  # Make sure this matches your LoRa module's setting

# === Setup Serial ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.5)

# Setup terminal for non-blocking input (optional)
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

# === Receiver Loop ===
def receive_loop():
    try:
        print("USB-TO-LoRa-HF Receiver Started")
        print("Press ESC to exit.\n")

        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting)
                if data:
                    # Print raw hex + ASCII (starting from byte 6)
                    print(f"[Received] {data.hex()}  |  {data[6:].decode(errors='replace')}")
            # Exit on ESC key
            if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                if sys.stdin.read(1) == '\x1b':  # ESC
                    break
            time.sleep(0.05)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        ser.close()
        print("\n[Exited]")

# === Start ===
if __name__ == "__main__":
    import select
    receive_loop()

