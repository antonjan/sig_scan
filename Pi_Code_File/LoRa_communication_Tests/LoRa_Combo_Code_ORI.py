import sx126x
import time
import random
import re
from datetime import datetime
from flask import Flask, render_template, jsonify
import threading
import paho.mqtt.client as mqtt

# MQTT Settings (same as original)
MQTT_BROKER = "iot.giga.co.za"
MQTT_PORT = 1883
MQTT_USERNAME = "homeassistant"
MQTT_PASSWORD = "h0m3@ss1$tant"
MQTT_TOPIC = "sig_scan/alert"

# Initialize LoRa node (adjust serial_num as needed)
node = sx126x.sx126x(serial_num="/dev/ttyS0", freq=868, addr=0, power=22, rssi=True, air_speed=2400, relay=False)

# Simulated LoRa packet header
HEADER = bytes([255, 255, 18, 255, 255, 12])

# Store alerts locally for web display
alerts = []
alerts_lock = threading.Lock()

# Setup Flask App
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alerts")
def get_alerts():
    return jsonify(alerts[-100:])  # Send last 100 alerts

def simulate_and_send():


    while True:
        received = node.receive()
        if received:
            try:
                print(f"Raw bytes: {received}")

                matches = pattern.findall(received)
                print(f"Matched alerts: {matches}")

                with alerts_lock:
                    for band, freq in matches:
                        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                        alerts.append((band.decode(), freq.decode(), timestamp))
                        print(f"[{timestamp}] ALERT: Band={band.decode()}, Freq={freq.decode()}")
                        send_mqtt_alert()
                    if len(alerts) > 20:
                        alerts[:] = alerts[-20:]

            except Exception as e:
                print(f"Error processing message: {e}")

# Start LoRa listener thread
        # Keep recent only
        if len(alerts) > 100:
            alerts.pop(0)

        # Send to MQTT (unchanged)
        # alert_message = f"ALERT_{band.decode()}:{freq.decode()}MHz".encode()
        

        time.sleep(2)

# Start LoRa listener thread
threading.Thread(target=simulate_and_send, daemon=True).start()

def send_mqtt_alert():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pattern = re.compile(b'ALERT_([2-5]G):(\d+MHz)')  # Byte pattern match
    matches = pattern.findall(received)
    mqtt_client.publish(MQTT_TOPIC, matches)
    print(f"[SENT] {matches} at {timestamp}")

def start_simulation():
    t = threading.Thread(target=simulate_and_send)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    start_simulation()
    app.run(host="0.0.0.0", port=5000)
