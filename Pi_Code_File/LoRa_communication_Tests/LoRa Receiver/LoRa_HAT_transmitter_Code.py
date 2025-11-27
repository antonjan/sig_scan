#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import time
import sx126x

# Create the LoRa node
# /dev/ttyS0 is the UART port typically used on the Pi Zero/3/4
# freq = 868 for 868 MHz band
# addr = 0 is the node address
# power = 22 is the transmit power in dBm
node = sx126x.sx126x(serial_num="/dev/ttyS0", freq=868, addr=0, power=22, rssi=True, air_speed=2400, relay=False)

# Broadcast address (send to all nodes)
dest_addr = 0xFFFF

# Calculate frequency offset from base (850 MHz for 868 band)
offset_freq = 868 - 850

try:
    print("Starting LoRa transmission every 2 seconds...")
    while True:
        message = "Hello from Pi!"

        # Create packet in required format
        data = bytes([dest_addr >> 8]) + bytes([dest_addr & 0xFF]) + \
               bytes([offset_freq]) + \
               bytes([node.addr >> 8]) + bytes([node.addr & 0xFF]) + \
               bytes([node.offset_freq]) + message.encode()

        node.send(data)
        print(f"Sent: {message}")
        time.sleep(2)

except KeyboardInterrupt:
    print("\nTransmission stopped.")

