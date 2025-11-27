import numpy as np
import time
from rtlsdr import RtlSdr
import sx126x

# LoRa HAT setup (adjust address/frequency if needed)
lora = sx126x.sx126x(
    serial_num="/dev/ttyS0",
    freq=868,
    addr=0,
    power=22,
    rssi=True,
    air_speed=2400,
    relay=False
)

# Frequency bands to scan (must be within RTL-SDR range: 24 MHz – 1766 MHz)
FREQUENCY_BANDS = {
    "2G": [(900e6, 950e6)],  # Removed 1800–1900 MHz
}

# Power threshold for alerting (in dB)
THRESHOLDS = {
    "2G": -50,
}

# Initialize RTL-SDR
sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.gain = 'auto'

# Check if frequency is supported by RTL-SDR
def is_supported_frequency(freq):
    return 24e6 <= freq <= 1766e6

def scan_band(freq_range, threshold, label):
    start_freq, end_freq = freq_range
    step_size = 2e6
    detected = False

    print(f"\nScanning {label} band: {start_freq/1e6:.1f}-{end_freq/1e6:.1f} MHz...")
    
    for freq in np.arange(start_freq, end_freq, step_size):
        if not is_supported_frequency(freq):
            print(f"{label} - {freq/1e6:.1f} MHz: Skipped (unsupported frequency)")
            continue

        try:
            sdr.center_freq = freq
            samples = sdr.read_samples(256 * 1024)
            power = 10 * np.log10(np.mean(np.abs(samples)**2))
            print(f"{label} - {freq/1e6:.1f} MHz: Power = {power:.2f} dB")

            if power > threshold:
                print(f"ALERT: Strong {label} signal detected at {freq/1e6:.1f} MHz!")
                alert_message = f"ALERT_{label}:{int(freq/1e6)}MHz".encode()
                data = bytes([255, 255, 18, 255, 255, 12]) + alert_message
                lora.send(data)
                detected = True

        except Exception as e:
            print(f"SDR Error at {freq/1e6:.1f} MHz: {e}")
            continue

    return detected

def main():
    print("Starting SDR + LoRa Alert System...")
    while True:
        for band, freq_ranges in FREQUENCY_BANDS.items():
            for freq_range in freq_ranges:
                scan_band(freq_range, THRESHOLDS[band], band)
        time.sleep(5)

# Entry point
try:
    main()
except KeyboardInterrupt:
    print("Stopping...")
    sdr.close()

