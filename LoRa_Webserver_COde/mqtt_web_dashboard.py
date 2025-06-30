from flask import Flask, jsonify, render_template
import threading
import time
import paho.mqtt.client as mqtt
from datetime import datetime

app = Flask(__name__)

# Store alerts here
alerts = []

# MQTT Configuration
MQTT_BROKER = "iot.giga.co.za"
MQTT_PORT = 1883
MQTT_USERNAME = "homeassistant"
MQTT_PASSWORD = "h0m3@ss1$tant"
MQTT_TOPIC = "sig_scan/alert"

# MQTT callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        # Expecting format: ALERT_2G:915MHz
        alert_type, freq = payload.split(":")
        freq = freq.replace("MHz", "")
        trigger_level = "-50"  # Hardcoded or map this per band
        alerts.append({
            "alert": alert_type,
            "frequency": freq,
            "trigger_level": trigger_level,
            "timestamp": timestamp
        })
    except Exception as e:
        print(f"Malformed message: {payload} -> {e}")

# MQTT setup in background
def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe(MQTT_TOPIC)
    client.loop_forever()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/alerts")
def get_alerts():
    return jsonify(alerts[-100:])  # Last 100 alerts

if __name__ == "__main__":
    t = threading.Thread(target=mqtt_thread)
    t.daemon = True
    t.start()
    app.run(host="0.0.0.0", port=5000)

