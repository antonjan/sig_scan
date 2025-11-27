import serial
import time

def configure_lora_module(port='/dev/ttyACM3', baudrate=115200):

    # Use ttyACM1 now
    ser = serial.Serial(
    port='/dev/ttyACM3',
    baudrate=115200,
    timeout=2,
    parity=serial.PARITY_NONE
    )
    time.sleep(2)  # wait for the module to be ready

    ser.write(b'AT+EXIT\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+EXIT: {response.strip()}")

    # Enter AT mode
    ascii_command = "+++\r\n"
    ser.write(ascii_command.encode('utf-8'))
    print(ascii_command.encode('utf-8'))
    time.sleep(1.5)
    response = ser.read_all()
    print(f"Response to +++: {response.strip()}")

    # ser.write('AT+BAUD=115200\r\n')


    # Try version command
    ser.write(b'AT+VER\r\n')
    time.sleep(1.5)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+VER: {response.strip()}")


    # Spreading Factor 7
    ser.write(b'AT+SF=7\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+SF: {response.strip()}")

    # Bandwidth 125 kHz
    ser.write(b'AT+BW=0\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+BW: {response.strip()}")

    # Coding Rate 4/5
    ser.write(b'AT+CR=1\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+CR: {response.strip()}")

    #send_cmd('AT+PWR=22')         # Max Power
    #ser.write(b'AT+PWR=22\r\n')
    #time.sleep(1)
    #response = ser.read_all().decode(errors='ignore')
    #print(f"Response to AT+PWR: {response.strip()}")

    #send_cmd('AT+NETID=0')        # Network ID 0
    #ser.write(b'AT+NETID=0\r\n')
    #time.sleep(1)
    #response = ser.read_all().decode(errors='ignore')
    #print(f"Response to AT+NETID: {response.strip()}")

    #send_cmd('AT+ADDR=0')         # Address 0
    ser.write(b'AT+ADDR=0\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+ADDR: {response.strip()}")

    #send_cmd('AT+TXCH=18')        # Transmit on channel 18 (? 868MHz)
    ser.write(b'AT+TXCH=18\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+TXCH: {response.strip()}")

    #send_cmd('AT+RXCH=18')        # Receive on channel 18
    ser.write(b'AT+RXCH=18\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+RXCH: {response.strip()}")

    #send_cmd('AT+MODE=1')         # Stream mode
    #ser.write(b'AT+MODE=1\r\n')
    #time.sleep(1)
    #response = ser.read_all().decode(errors='ignore')
    #print(f"Response to AT+MODE: {response.strip()}")

    #send_cmd('AT+RSSI=1')         # Enable RSSI reporting (optional)
    ser.write(b'AT+RSSI=1\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+RSSI: {response.strip()}")

    #send_cmd('AT+PORT=3')         # UART mode (RS232)
    ser.write(b'AT+PORT=3\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+PORT: {response.strip()}")

    #send_cmd('AT+BAUD=115200')    # Match your serial port baud rate
    #ser.write(b'AT+BAUD=115200\r\n')
    #time.sleep(1)
    #response = ser.read_all().decode(errors='ignore')
    #print(f"Response to AT+BAUD: {response.strip()}")

    #send_cmd('AT+COMM="8N1"') 
    #ser.write(b'AT+COMM="8N1"\r\n')
    #time.sleep(1)
    #response = ser.read_all().decode(errors='ignore')
    #print(f"Response to AT+COMM: {response.strip()}")

    # Exit AT mode command
    ser.write(b'AT+EXIT\r\n')
    time.sleep(1)
    response = ser.read_all().decode(errors='ignore')
    print(f"Response to AT+EXIT: {response.strip()}")

    return ser

def listen_for_messages(ser):
    """
    Listens for incoming LoRa messages and prints them.
    """
    print("Listening for incoming LoRa messages... (press Ctrl+C to quit)")
    try:
        while True:
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                if data:
                    print(f"Received: {data.decode(errors='ignore').strip()}")
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Listener stopped by user.")
    finally:
        ser.close()

if __name__ == "__main__":
    serial_port = '/dev/ttyACM0'  # Update this if your device is on a different port
    ser = configure_lora_module(port=serial_port)
    listen_for_messages(ser)




