import numpy as np
import time
from rtlsdr import RtlSdr

# Define frequency bands (in Hz) for different technologies
FREQUENCY_BANDS = {
    "2G": [(900e6, 950e6), (1800e6, 1900e6)]#,
#    "3G": [(1920e6, 2170e6)],
#    "4G": [(2300e6, 2700e6)],
#    "5G": [(3300e6, 3800e6), (24e9, 28e9)]  # Sub-6GHz and mmWave (if RTL-SDR supports it)
}

# Define power thresholds (in dB) for detection
THRESHOLDS = {
    "2G": -50#,
#    "3G": -50,
#    "4G": -55,
#    "5G": -60
}

# RTL-SDR configuration
sdr = RtlSdr()
sdr.sample_rate = 2.4e6  # 2.4 MSPS
sdr.gain = 'auto'  # Adjust automatically

def scan_band(freq_range, threshold, label):
    """Scans a given frequency range and detects strong signals."""
    start_freq, end_freq = freq_range
    step_size = 2e6  # 2 MHz steps
    detected = False
    
    print(f"Scanning {label} band: {start_freq/1e6}-{end_freq/1e6} MHz...")
    
    for freq in np.arange(start_freq, end_freq, step_size):
        sdr.center_freq = freq
        samples = sdr.read_samples(256*1024)  # Read samples
        power = 10 * np.log10(np.mean(np.abs(samples)**2))  # Calculate power in dB
        
        print(f"{label} - {freq/1e6} MHz: Power = {power:.2f} dB")
        
        if power > threshold:
            print(f"ALERT: Strong {label} signal detected at {freq/1e6} MHz!")
            detected = True
    
    return detected

def main():
    print("Starting GSM Frequency Scanner...")
    while True:
        for band, freq_ranges in FREQUENCY_BANDS.items():
            for freq_range in freq_ranges:
                if scan_band(freq_range, THRESHOLDS[band], band):
                    print(f"Possible mobile phone detected in {band} band!")
        time.sleep(5)  # Pause before rescanning

try:
    main()
except KeyboardInterrupt:
    print("Stopping scanner...")
    sdr.close()

