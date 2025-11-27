import sys
import sx126x
import time
import select
import termios
import tty
import json
import threading
from flask import Flask, jsonify, render_template

# Flask app
app = Flask(__name__)
alert_log = []  # Store recent alerts here (max 100)

# Set up LoRa module
node = sx126x.sx126x(serial_num="/dev/ttyS0", freq=868, addr=65535, power=22, rssi=True, air_speed=2400, relay=False)
LORA_PREFIX = b'\xff\xff\x0c'

# Terminal settings for keypress detection
old_settings = termios.tcgetattr(sys.stdin)
tty.setcbreak(sys.stdin.fileno())

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/alerts')
def get_alerts():
    # Return recent alerts (reversed for newest first)
    return jsonify(alert_log[::-1])

# LoRa helper functions
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
                    alert = {
                        "alert": msg["alert"]["Band"],
                        "frequency": msg["alert"]["Freq"],
                        "trigger_level": msg["alert"]["DBi"],
                        # "avgDBi": msg["alert"]["AvgDBi"],
                        "timestamp": msg["alert"]["timestamp"]
                    }
                    # Add to alert log (keep only last 100)
                    alert_log.append(alert)
                    if len(alert_log) > 100:
                        alert_log.pop(0)

                    print(f"\n[ALERT RECEIVED]")
                    print(json.dumps(alert, indent=4))
                except Exception as e:
                    print(f"[ERROR] Failed to handle message: {e}")
                    print(f"Raw msg: {msg}")
        time.sleep(0.1)

def listen_for_exit():
    print("Listening for LoRa alerts... Press Esc to stop.")
    while True:
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            if sys.stdin.read(1) == '\x1b':
                print("Exiting...")
                break
        time.sleep(0.1)

# Start threads
receiver_thread = threading.Thread(target=receive_lora, daemon=True)
receiver_thread.start()

# Start Flask app in a separate thread
flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000), daemon=True)
flask_thread.start()

try:
    listen_for_exit()
finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
