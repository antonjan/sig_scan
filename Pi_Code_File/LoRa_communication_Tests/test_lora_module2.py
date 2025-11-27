import serial
import time

ser = serial.Serial('/dev/ttyACM1', 115200, timeout=1)
time.sleep(2)

print("Listening for LoRa messages...\n")

try:
    while True:
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode(errors='ignore').strip()
            if data:
                print(f"Received: {data}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    ser.close()

