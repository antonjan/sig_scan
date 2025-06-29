import sx126x
import threading
import time
import re
from flask import Flask, render_template_string

# Initialize LoRa node (adjust serial_num as needed)
node = sx126x.sx126x(
    serial_num="/dev/ttyS0",  # Change if you're using a different port
    freq=868,
    addr=0,
    power=22,
    rssi=True,
    air_speed=2400,
    relay=False
)

# Shared alert list and threading lock
alerts = []
alerts_lock = threading.Lock()

# HTML template with auto-refresh and alert display
html_template = """
<!doctype html>
<html>
<head>
    <title>SDR LoRa Alerts</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { font-family: Arial; background-color: #f4f4f4; padding: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px 12px; border: 1px solid #aaa; text-align: center; }
        th { background-color: #444; color: white; }
        tr:nth-child(even) { background-color: #eee; }
    </style>
</head>
<body>
    <h1>Received SDR Alerts</h1>
    <table>
        <tr><th>Band</th><th>Frequency</th><th>Time</th></tr>
        {% for band, freq, timestamp in alerts %}
        <tr><td>{{ band }}</td><td>{{ freq }}</td><td>{{ timestamp }}</td></tr>
        {% else %}
        <tr><td colspan="3">No alerts received yet.</td></tr>
        {% endfor %}
    </table>
</body>
</html>
"""

# Flask app
app = Flask(__name__)

@app.route("/")
def index():
    with alerts_lock:
        recent_alerts = alerts[::-1]  # Show newest first
    return render_template_string(html_template, alerts=recent_alerts)

# LoRa receiving thread
def lora_listener():
    pattern = re.compile(b'ALERT_([2-5]G):(\d+MHz)')  # Byte pattern match

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
                    if len(alerts) > 20:
                        alerts[:] = alerts[-20:]

            except Exception as e:
                print(f"Error processing message: {e}")

# Start LoRa listener thread
threading.Thread(target=lora_listener, daemon=True).start()

# Run web server
if __name__ == "__main__":
    print("Receiver and web server running on http://<your-pi-ip>:8080")
    app.run(host="0.0.0.0", port=8080)

