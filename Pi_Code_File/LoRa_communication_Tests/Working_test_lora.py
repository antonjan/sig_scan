import serial
import time

# Use ttyACM1 now
ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate=115200,
    timeout=2,
    parity=serial.PARITY_NONE
)
time.sleep(2)  # wait for the module to be ready

# Enter AT mode
ascii_command = "+++\r\n"
ser.write(ascii_command.encode('utf-8'))
print(ascii_command.encode('utf-8'))
time.sleep(1)
response = ser.read_all()
print(f"Response to +++: {response.strip()}")

# ser.write('AT+BAUD=115200\r\n')


# Try version command
ser.write(b'AT+VER\r\n')
time.sleep(1)
response = ser.read_all().decode(errors='ignore')
print(f"Response to AT+VER: {response.strip()}")


ser.write(b'AT+EXIT\r\n')
time.sleep(1)
response = ser.read_all().decode(errors='ignore')
print(f"Response to AT+EXIT: {response.strip()}")


ser.close()



