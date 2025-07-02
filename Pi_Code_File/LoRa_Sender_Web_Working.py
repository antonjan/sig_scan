import numpy as np
import time
import threading
from flask import Flask, request, render_template_string
from rtlsdr import RtlSdr
import sx126x
from datetime import datetime
import json

# LoRa setup
lora = sx126x.sx126x(
    serial_num="/dev/ttyS0",
    freq=868,
    addr=0,
    power=22,
    rssi=True,
    air_speed=2400,
    relay=False
)

FREQUENCY_BANDS = {
    "2G": [(900e6, 950e6), (1800e6, 1900e6)],
    "3G": [(1920e6, 2170e6)],
    "4G": [(2300e6, 2700e6)],
    "5G": [(3300e6, 3800e6)]
}

DEFAULT_THRESHOLDS = {
    "2G": -15,
    "3G": -15,
    "4G": -15,
    "5G": -16
}

power_history = {band: [] for band in FREQUENCY_BANDS}
manual_thresholds = DEFAULT_THRESHOLDS.copy()
trigger_mode = {'mode': 'auto'}  # Can be 'auto' or 'manual'
margin_db = 3

sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.gain = 'auto'

# Web server using Flask
app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trigger Mode Control</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #121212;
            color: #f1f1f1;
            margin: 0;
            padding: 1rem;
        }

        h2 {
            text-align: center;
            margin-top: 0;
        }

        form {
            max-width: 400px;
            margin: 1rem auto;
            background: #1e1e1e;
            padding: 1rem;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }

        label {
            display: block;
            margin: 0.5rem 0 0.2rem;
        }

        input[type="text"] {
            width: 100%;
            padding: 0.5rem;
            margin-bottom: 0.8rem;
            border: none;
            border-radius: 5px;
            background-color: #2e2e2e;
            color: #fff;
        }

        button {
            width: 100%;
            padding: 0.75rem;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1rem;
            cursor: pointer;
            margin-top: 0.5rem;
        }

        button:hover {
            background-color: #45a049;
        }

        .footer {
            text-align: center;
            font-size: 0.8rem;
            color: #888;
            margin-top: 2rem;
        }
    </style>
</head>
<body>
    <h2>Trigger Mode: {{ mode.upper() }}</h2>
    
    <form method="post" action="/toggle">
        <button type="submit">Switch to {{ 'Manual' if mode == 'auto' else 'Auto' }}</button>
    </form>

    {% if mode == 'manual' %}
    <form method="post" action="/set_thresholds">
        {% for band in bands %}
            <label>{{ band }} Threshold (dB):</label>
            <input type="text" name="{{ band }}" value="{{ thresholds[band] }}">
        {% endfor %}
        <button type="submit">Update Thresholds</button>
    </form>
    {% endif %}

    <div class="footer">LoRa SDR Control Panel · Pi Zero 2 W</div>
</body>
</html>
"""


@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE, mode=trigger_mode['mode'],
                                  bands=FREQUENCY_BANDS.keys(),
                                  thresholds=manual_thresholds)

@app.route("/toggle", methods=["POST"])
def toggle_mode():
    trigger_mode['mode'] = 'manual' if trigger_mode['mode'] == 'auto' else 'auto'
    return home()

@app.route("/set_thresholds", methods=["POST"])
def set_thresholds():
    for band in FREQUENCY_BANDS.keys():
        try:
            manual_thresholds[band] = float(request.form[band])
        except ValueError:
            pass  # Ignore invalid input
    return home()

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

def scan_band(freq_range, label):
    start_freq, end_freq = freq_range
    step_size = 2e6
    detected = False
    powers = []

    for freq in np.arange(start_freq, end_freq, step_size):
        sdr.center_freq = freq
        samples = sdr.read_samples(256*1024)
        power = 10 * np.log10(np.mean(np.abs(samples)**2))
        powers.append(power)

        if trigger_mode['mode'] == 'manual':
            threshold = manual_thresholds[label]
        else:
            avg_power = (sum(power_history[label]) / len(power_history[label])) if power_history[label] else DEFAULT_THRESHOLDS[label]
            threshold = avg_power + margin_db

        if power > threshold:
            alert_data = {
                "alert": {
                    "Band": label,
                    "Freq": f"{int(freq/1e6)}MHz",
                    "DBi": round(power, 2),
                    "Threshold": round(threshold, 2),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            alert_message = json.dumps(alert_data).encode('utf-8')
            data = bytes([255, 255, 18, 255, 255, 12]) + alert_message
            lora.send(data)
            print(f"ALERT: {label} {freq/1e6}MHz > {threshold:.2f}dB")
            detected = True

    power_history[label].extend(powers)
    if len(power_history[label]) > 100:
        power_history[label] = power_history[label][-100:]
    return detected

def main_loop():
    print("Starting SDR + LoRa Alert System...")
    while True:
        for band, freq_ranges in FREQUENCY_BANDS.items():
            for freq_range in freq_ranges:
                scan_band(freq_range, band)
        time.sleep(5)

# --- Run the server and scanning loop in parallel ---
if __name__ == "__main__":
    try:
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        main_loop()
    except KeyboardInterrupt:
        print("Stopping...")
        sdr.close()
