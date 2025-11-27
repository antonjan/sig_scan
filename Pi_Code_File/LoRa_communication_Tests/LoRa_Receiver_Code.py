import time
import sx126x
import random
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

# Setup Flask App
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alerts")
def get_alerts():
    return jsonify(alerts[-100:])  # Send last 100 alerts

def simulate_and_send():
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()

    while True:
        band = "2G"
        freq = random.choice([900, 915, 1800, 1850])  # MHz
        alert_message = f"ALERT_{band}:{freq}MHz".encode()
        full_packet = HEADER + alert_message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add to web dashboard
        alerts.append({
            "alert": f"ALERT_{band}",
            "frequency": str(freq),
            "trigger_level": "-50",
            "timestamp": timestamp
        })

        # Keep recent only
        if len(alerts) > 100:
            alerts.pop(0)

        # Send to MQTT (unchanged)
        mqtt_client.publish(MQTT_TOPIC, alert_message)
        print(f"[SENT to MQTT] {alert_message.decode()} at {timestamp}")

        time.sleep(2)

def start_simulation():
    t = threading.Thread(target=simulate_and_send)
    t.daemon = True
    t.start()

if __name__ == "__main__":
    start_simulation()
    app.run(host="0.0.0.0", port=5000)

