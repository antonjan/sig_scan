import numpy as np
import time
import threading
from flask import Flask, request, render_template_string
from rtlsdr import RtlSdr
import sx126x
from datetime import datetime
import json
import os

# === CONFIG FILE PATH ===
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

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
    "2G_LOW": [(900e6, 950e6)],
    "2G_HIGH": [(1800e6, 1900e6)],
    "3G": [(1920e6, 2170e6)],
    "4G": [(2300e6, 2700e6)],
    "5G": [(3300e6, 3800e6)]
}

DEFAULT_THRESHOLDS = {
    "2G_LOW": -8,
    "2G_HIGH": -8,
    "3G": -10,
    "4G": -10,
    "5G": -10
}

power_history = {band: [] for band in FREQUENCY_BANDS}
manual_thresholds = DEFAULT_THRESHOLDS.copy()
auto_margins = {band: 2.0 for band in FREQUENCY_BANDS}
trigger_mode = {'mode': 'auto'}

scan_stats = {
    band: {"avg": None, "max": None, "min": None}
    for band in FREQUENCY_BANDS
}

# === CONFIG LOAD/SAVE ===
def save_config():
    config = {
        "trigger_mode": trigger_mode['mode'],
        "manual_thresholds": manual_thresholds,
        "auto_margins": auto_margins
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print("[CONFIG] Saved to config.json")

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            trigger_mode['mode'] = config.get("trigger_mode", "auto")
            manual_thresholds.update(config.get("manual_thresholds", {}))
            auto_margins.update(config.get("auto_margins", {}))
        print("[CONFIG] Loaded from config.json")
    except FileNotFoundError:
        print("[CONFIG] config.json not found, using defaults")

# === Load configuration on startup ===
load_config()

sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.gain = 'auto'

app = Flask(__name__)

HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="10">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Trigger Mode Control</title>
  <style>
    body { font-family: sans-serif; background-color: #121212; color: #f1f1f1; margin: 0; padding: 1rem; }
    h2, h3 { text-align: center; }
    form { max-width: 400px; margin: 1rem auto; background: #1e1e1e; padding: 1rem; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.5); }
    label { display: block; margin-top: 1rem; }
    input[type="text"] { width: 100%; padding: 0.5rem; border: 1px solid #555; border-radius: 5px; background-color: #2c2c2c; color: #fff; }
    button { width: 100%; padding: 0.75rem; margin-top: 1rem; background-color: #4CAF50; color: white; border: none; border-radius: 5px; font-size: 1rem; cursor: pointer; }
    button:hover { background-color: #45a049; }
    table { margin: 1rem auto; border-collapse: collapse; width: 80%; }
    th, td { border: 1px solid #444; padding: 0.5rem; text-align: center; }
    th { background-color: #222; }
    .footer { text-align: center; font-size: 0.8rem; margin-top: 2rem; color: #888; }
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
      <label>{{ band }} Manual Threshold (dB):</label>
      <input type="text" name="{{ band }}" value="{{ thresholds[band] }}">
    {% endfor %}
    <button type="submit">Update Manual Thresholds</button>
  </form>
  {% endif %}

  <form method="post" action="/set_margins">
    {% for band in bands %}
      <label>{{ band }} Auto Margin (dB):</label>
      <input type="text" name="{{ band }}" value="{{ margins[band] }}">
    {% endfor %}
    <button type="submit">Update Auto Margins</button>
  </form>

  <h3>Current Scan Statistics</h3>
  <table>
    <tr>
      <th>Band</th>
      <th>Avg dB</th>
      <th>Max dB</th>
      <th>Min dB</th>
    </tr>
    {% for band in bands %}
    <tr>
      <td>{{ band }}</td>
      <td>{{ stats[band]['avg'] if stats[band]['avg'] is not none else 'N/A' }}</td>
      <td>{{ stats[band]['max'] if stats[band]['max'] is not none else 'N/A' }}</td>
      <td>{{ stats[band]['min'] if stats[band]['min'] is not none else 'N/A' }}</td>
    </tr>
    {% endfor %}
  </table>

  <div class="footer">SDR Trigger Control Panel</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(
        HTML_TEMPLATE,
        mode=trigger_mode['mode'],
        bands=FREQUENCY_BANDS.keys(),
        thresholds=manual_thresholds,
        margins=auto_margins,
        stats=scan_stats
    )

@app.route("/toggle", methods=["POST"])
def toggle_mode():
    trigger_mode['mode'] = 'manual' if trigger_mode['mode'] == 'auto' else 'auto'
    save_config()
    return home()

@app.route("/set_thresholds", methods=["POST"])
def set_thresholds():
    for band in FREQUENCY_BANDS.keys():
        try:
            manual_thresholds[band] = float(request.form[band])
        except ValueError:
            pass
    save_config()
    return home()

@app.route("/set_margins", methods=["POST"])
def set_margins():
    for band in FREQUENCY_BANDS.keys():
        try:
            auto_margins[band] = float(request.form[band])
        except ValueError:
            pass
    save_config()
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

        print(f"Scanning {label}: {freq/1e6:.2f} MHz — Power = {power:.2f} dB")

        if trigger_mode['mode'] == 'manual':
            threshold = manual_thresholds[label]
        else:
            avg_power = (sum(power_history[label]) / len(power_history[label])) if power_history[label] else DEFAULT_THRESHOLDS[label]
            threshold = avg_power + auto_margins[label]

        if power > threshold:
            alert_data = {
                "alert": {
                    "Band": "2G" if label.startswith("2G_") else label,
                    "Freq": f"{int(freq/1e6)}MHz",
                    "DBi": round(power, 2),
                    "Threshold": round(threshold, 2),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            alert_message = json.dumps(alert_data).encode('utf-8')
            data = bytes([255, 255, 18, 255, 255, 12]) + alert_message
            lora.send(data)
            print(f"ALERT: {label} Strong Signal Detected {freq/1e6}MHz > {threshold:.2f}dB")
            detected = True

    power_history[label] = powers

    if powers:
        avg_dbi = round((sum(powers) / len(powers)) + auto_margins[label], 2)
        max_dbi = round(max(powers), 2)
        min_dbi = round(min(powers), 2)

        scan_stats[label]["avg"] = avg_dbi
        scan_stats[label]["max"] = max_dbi
        scan_stats[label]["min"] = min_dbi

        summary_data = {
            "scan_summary": {
                "Band": "2G" if label.startswith("2G_") else label,
                "avgDBi": avg_dbi,
                "maxDBi": max_dbi,
                "minDBi": min_dbi,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        summary_message = json.dumps(summary_data).encode('utf-8')
        data = bytes([255, 255, 18, 255, 255, 12]) + summary_message

        time.sleep(0.2)
        lora.send(data)
        print(f"SUMMARY: {label} — Avg: {avg_dbi:.2f} dB, Max: {max_dbi:.2f} dB, Min: {min_dbi:.2f} dB")
        time.sleep(1)

    return detected

def main_loop():
    print("Starting SDR + LoRa Alert System...")
    while True:
        for band, freq_ranges in FREQUENCY_BANDS.items():
            for freq_range in freq_ranges:
                scan_band(freq_range, band)
        time.sleep(5)

if __name__ == "__main__":
    try:
        web_thread = threading.Thread(target=run_web_server, daemon=True)
        web_thread.start()
        main_loop()
    except KeyboardInterrupt:
        print("Stopping...")
        sdr.close()
