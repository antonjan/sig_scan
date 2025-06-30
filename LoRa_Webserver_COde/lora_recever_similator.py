import time
import random

# Example LoRa packet format from transmitter
# bytes([255, 255, 18, 255, 255, 12]) + alert_message
HEADER = bytes([255, 255, 18, 255, 255, 12])

def simulate_receive():
    bands = ["2G"]
    freqs = [random.choice([900, 915, 1800, 1850]) for _ in range(5)]  # MHz

    for freq in freqs:
        band = "2G"
        alert_message = f"ALERT_{band}:{freq}MHz".encode()
        full_packet = HEADER + alert_message
        yield full_packet

def parse_packet(packet):
    if packet.startswith(HEADER):
        alert = packet[len(HEADER):].decode()
        print(f"[LoRa Receiver] Received Alert: {alert}")
    else:
        print("[LoRa Receiver] Unknown or malformed packet")

def main():
    print("Starting Simulated LoRa Receiver...")
    while True:
        for packet in simulate_receive():
            parse_packet(packet)
            time.sleep(2)  # Simulate delay between packets

try:
    main()
except KeyboardInterrupt:
    print("Simulation stopped.")

