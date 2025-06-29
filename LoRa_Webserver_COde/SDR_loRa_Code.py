import numpy as np
import time
from rtlsdr import RtlSdr
import sx126x

# LoRa HAT setup (adjust address/frequency if needed)
lora = sx126x.sx126x(serial_num="/dev/ttyS0", freq=868, addr=0, power=22, rssi=True, air_speed=2400, relay=False)

FREQUENCY_BANDS = {
    "2G": [(900e6, 950e6), (1800e6, 1900e6)],
}

THRESHOLDS = {
    "2G": -50,
}

sdr = RtlSdr()
sdr.sample_rate = 2.4e6
sdr.gain = 'auto'

def scan_band(freq_range, threshold, label):
    start_freq, end_freq = freq_range
    step_size = 2e6
    detected = False

    print(f"Scanning {label} band: {start_freq/1e6}-{end_freq/1e6} MHz...")
    for freq in np.arange(start_freq, end_freq, step_size):
        sdr.center_freq = freq
        samples = sdr.read_samples(256*1024)
        power = 10 * np.log10(np.mean(np.abs(samples)**2))

        print(f"{label} - {freq/1e6} MHz: Power = {power:.2f} dB")

        if power > threshold:
            print(f"ALERT: Strong {label} signal detected at {freq/1e6} MHz!")
            alert_message = f"ALERT_{label}:{int(freq/1e6)}MHz".encode()

            # send as broadcast on freq offset
            data = bytes([255, 255, 18, 255, 255, 12]) + alert_message
            lora.send(data)
            detected = True

    return detected

def main():
    print("Starting SDR + LoRa Alert System...")
    while True:
        for band, freq_ranges in FREQUENCY_BANDS.items():
            for freq_range in freq_ranges:
                scan_band(freq_range, THRESHOLDS[band], band)
        time.sleep(5)

try:
    main()
except KeyboardInterrupt:
    print("Stopping...")
    sdr.close()

