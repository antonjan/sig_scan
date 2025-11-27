#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import serial

# Replace this with your actual serial port
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200 # Most USB LoRa modules use 9600, but check your datasheet

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Listening for LoRa data on {SERIAL_PORT} at {BAUD_RATE} baud...\nPress Ctrl+C to stop.\n")

    while True:
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print(f"Received: {line}")

except serial.SerialException as e:
    print(f"Serial port error: {e}")
except KeyboardInterrupt:
    print("\nStopped.")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()

