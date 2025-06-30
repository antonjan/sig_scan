import time
import random
import paho.mqtt.client as mqtt
# pip3 install paho-mqtt
# MQTT Settings
MQTT_BROKER = "iot.giga.co.za"         # Change to your broker IP or hostname
MQTT_PORT = 1883
MQTT_USERNAME = "homeassistant"   # Replace with your MQTT username
MQTT_PASSWORD = "h0m3@ss1$tant"   # Replace with your MQTT password
MQTT_TOPIC = "sig_scan/sig"

# LoRa packet header (as per your transmitter)
HEADER = bytes([255, 255, 18, 255, 255, 12])

# MQTT Client Setup
mqtt_client = mqtt.Client()

# Set username and password for broker authentication
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

# Connect and start loop
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()

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
        
        # Publish to MQTT
        mqtt_client.publish(MQTT_TOPIC, alert)
        print(f"[MQTT] Published to topic '{MQTT_TOPIC}': {alert}")
    else:
        print("[LoRa Receiver] Unknown or malformed packet")

def main():
    print("Starting Simulated LoRa Receiver with MQTT (auth)...")
    while True:
        for packet in simulate_receive():
            parse_packet(packet)
            time.sleep(2)  # Simulate delay between packets

try:
    main()
except KeyboardInterrupt:
    print("Simulation stopped.")
    mqtt_client.loop_stop()
    mqtt_client.disconnect()

