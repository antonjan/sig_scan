import serial
import time

# Open the serial port for the USB LoRa module
ser = serial.Serial('/dev/ttyACM1', 115200, timeout=2)
time.sleep(2)

def send_cmd(cmd):
    print(f"Sending: {cmd.strip()}")
    ser.write((cmd + '\r\n').encode())
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore').strip()
    print(f"Response: {response}\n")

# Enter AT mode
ser.write(b'+++\r\n')
time.sleep(1)
print("Entered AT mode:")
print(ser.read_all().decode(errors='ignore').strip(), '\n')

# Disable command echo for cleaner responses
send_cmd('ATE=0')

# Set matching parameters
send_cmd('AT+SF=7')           # Spreading Factor 7
send_cmd('AT+BW=0')           # Bandwidth 125 kHz
send_cmd('AT+CR=1')           # Coding Rate 4/5
send_cmd('AT+PWR=22')         # Max Power
send_cmd('AT+NETID=0')        # Network ID 0
send_cmd('AT+ADDR=0')         # Address 0
send_cmd('AT+TXCH=18')        # Transmit on channel 18 (? 868MHz)
send_cmd('AT+RXCH=18')        # Receive on channel 18
send_cmd('AT+MODE=1')         # Stream mode
send_cmd('AT+RSSI=1')         # Enable RSSI reporting (optional)
send_cmd('AT+PORT=3')         # UART mode (RS232)
send_cmd('AT+BAUD=115200')    # Match your serial port baud rate
send_cmd('AT+COMM="8N1"')     # 8 data bits, no parity, 1 stop bit

# Exit AT mode
send_cmd('AT+EXIT')

ser.close()

