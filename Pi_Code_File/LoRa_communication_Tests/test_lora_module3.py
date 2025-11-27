import serial
import time

# Use ttyACM1 now
ser = serial.Serial('/dev/ttyACM1', 9600, timeout=2)
time.sleep(2)  # wait for the module to be ready

# Enter AT mode
ser.write(b'+++\r\n')
time.sleep(1)
response = ser.read_all().decode(errors='ignore')
print(f"Response to +++: {response.strip()}")

# Try version command
ser.write(b'AT+VER\r\n')
time.sleep(1)
response = ser.read_all().decode(errors='ignore')
print(f"Response to AT+VER: {response.strip()}")

ser.close()
