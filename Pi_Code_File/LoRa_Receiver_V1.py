import sys
import sx126x
import time
import json
import threading
from flask import Flask, jsonify, render_template
from collections import defaultdict
import paho.mqtt.client as mqtt

# MQTT Settings
MQTT_BROKER = "iot.giga.co.za"
MQTT_PORT = 1883
MQTT_USERNAME = "homeassistant"
MQTT_PASSWORD = "h0m3@ss1$tant"
MQTT_TOPIC = "sig_scan/alert"

app = Flask(__name__)
alert_log = []  # last 100 alerts
avg_dbi_per_band = defaultdict(lambda: -10)  # fallback

# LoRa
node = sx126x.sx126x(
    serial_num="/dev/ttyS0",
    freq=868,
    addr=65535,
    power=22,
    rssi=True,
    air_speed=2400,
    relay=False
)
LORA_PREFIX = b'\xff\xff\x0c'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alerts')
def get_alerts():
    return jsonify(alert_log[::-1])

@app.route('/thresholds')
def get_thresholds():
    return jsonify(avg_dbi_per_band)

def extract_json_messages(data):
    messages = []
    parts = data.split(LORA_PREFIX)
    for part in parts[1:]:
        try:
            json_str = part.decode("utf-8", errors="ignore")
            start_idx = json_str.find("{")
            end_idx = json_str.rfind("}")
            if start_idx != -1 and end_idx != -1:
                clean_json = json_str[start_idx:end_idx + 1]
                obj = json.loads(clean_json)
                messages.append(obj)
        except Exception as e:
            print(f"[WARN] Failed to parse JSON: {e}")
    return messages

def receive_lora():
    while True:
        if node.ser.inWaiting() > 0:
            time.sleep(0.5)
            r_buff = node.ser.read(node.ser.inWaiting())
            messages = extract_json_messages(r_buff)
            for msg in messages:
                try:
                    if "alert" in msg:
                        alert = {
                            "alert": msg["alert"]["Band"],
                            "frequency": msg["alert"]["Freq"],
                            "trigger_level": msg["alert"]["DBi"],
                            "avgDBi": msg["alert"]["Threshold"],
                            "timestamp": msg["alert"]["timestamp"]
                        }
                        alert_log.append(alert)
                        if len(alert_log) > 100:
                            alert_log.pop(0)

                        print(f"\n[ALERT RECEIVED]")
                        print(json.dumps(alert, indent=4))
                        send_mqtt_alert(json.dumps(alert))

                    elif "scan_summary" in msg:
                        summary = msg["scan_summary"]
                        band = summary["Band"]
                        avg_dbi = summary["avgDBi"]
                        avg_dbi_per_band[band] = avg_dbi
                        print(f"[SUMMARY RECEIVED] {band} avgDBi={avg_dbi}")

                except Exception as e:
                    print(f"[ERROR] Failed to handle message: {e}")
                    print(f"Raw msg: {msg}")
        time.sleep(0.1)

def send_mqtt_alert(mqtt_data):
    mqtt_client = mqtt.Client()
    mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_start()
    mqtt_client.publish(MQTT_TOPIC, mqtt_data)
    mqtt_client.loop_stop()

# Threads
threading.Thread(target=receive_lora, daemon=True).start()
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True).start()

print("LoRa receiver and web server started. Running indefinitely.")
while True:
    time.sleep(1)
