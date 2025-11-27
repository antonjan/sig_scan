#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import serial
import threading
import time
import select
import termios
import tty
from threading import Timer
import os

# === USER CONFIGURATION ===
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200         # Adjust to match module config
MY_ADDR = 0              # Address of this node
FREQ_MHZ = 868           # Frequency in MHz
AIR_SPEED = 2400         # For documentation/reference only
TIMER_INTERVAL = 10      # Seconds for CPU temp broadcast

# === CALCULATED ===
OFFSET_FREQ = FREQ_MHZ - (850 if FREQ_MHZ > 850 else 410)

# === Serial Setup ===
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.5)
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

def get_cpu_temp():
    """Returns CPU temp in Celsius"""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return float(f.read()) / 1000.0
    except:
        return 0.0

def format_message(target_addr, payload):
    """Formats message in the same structure as HAT demo"""
    target_high = (target_addr >> 8) & 0xFF
    target_low  = target_addr & 0xFF
    my_high     = (MY_ADDR >> 8) & 0xFF
    my_low      = MY_ADDR & 0xFF

    msg = bytes([
        target_high, target_low, OFFSET_FREQ,
        my_high, my_low, OFFSET_FREQ
    ]) + payload.encode()
    return msg

def send_message(target_addr, payload):
    msg = format_message(target_addr, payload)
    ser.write(msg)
    print(f"[Sent] → {target_addr} : {payload}")

def send_deal():
    print("\nEnter string as: target_address,freq,message")
    print("Example: 0,868,Hello World")
    print("Input: ", end="", flush=True)

    input_str = ""
    while True:
        ch = sys.stdin.read(1)
        if ch == "\n":
            break
        input_str += ch
        sys.stdout.write(ch)
        sys.stdout.flush()

    try:
        parts = input_str.split(",")
        target = int(parts[0])
        msg = parts[2]
        send_message(target, msg)
    except:
        print("\n[Error] Invalid input format.")

def send_cpu_continue(continue_loop=True):
    global timer_task
    payload = f"Hello World" ## {get_cpu_temp():.2f} C"
    send_message(0xFFFF, payload)  # Broadcast
    if continue_loop:
        timer_task = Timer(TIMER_INTERVAL, send_cpu_continue)
        timer_task.start()

def receive_loop():
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting)
            if data:
                print(f"\n[Received] {data.hex()}  |  {data[6:].decode(errors='replace')}")
        time.sleep(0.1)

# === Main Event Loop ===
try:
    print("USB-TO-LoRa-HF Interface Started")
    print("Press [i] to send a message")
    print("Press [s] to send CPU temp every 10s")
    print("Press [Esc] to exit\n")

    # Start receiver in background
    threading.Thread(target=receive_loop, daemon=True).start()

    while True:
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            ch = sys.stdin.read(1)

            if ch == '\x1b':  # Esc
                break
            elif ch == 'i':
               print("Press [c] to stop sending temperature...")
               send_deal()
            elif ch == 's':
                print(" S Pressed")
                timer_task = Timer(TIMER_INTERVAL, send_cpu_continue)
                timer_task.start()
                while True:
                    if sys.stdin.read(1) == 'c':
                        timer_task.cancel()
                        print("\nStopped temperature broadcast.")
                        break

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    ser.close()
    print("\n[Exited]")

