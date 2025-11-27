import serial
import time

# Serial port configuration
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
TIMEOUT = 1  # seconds

def enter_at_mode(ser):
    print("Entering AT command mode...")
    ser.write(b'+++\r\n')
    time.sleep(1)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='replace').strip()
        print(f"Response: {response}")
        if "OK" in response or "AT" in response:
            return True
    return False

def check_device(ser):
    print("Checking device with AT+VER...")
    ser.write(b'AT+VER\r\n')
    time.sleep(0.5)
    if ser.in_waiting > 0:
        response = ser.read(ser.in_waiting).decode('utf-8', errors='replace').strip()
        print(f"Device responded with version: {response}")
        return True
    return False

def exit_at_mode(ser):
    ser.write(b'AT+EXIT\r\n')
    time.sleep(0.5)
    # Clear any remaining input
    ser.read(ser.in_waiting)

def listen_lora():
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT) as ser:
            time.sleep(1)  # Wait for device to be ready

            # Check device responsiveness
            if not enter_at_mode(ser):
                print("Failed to enter AT command mode.")
                return
            if not check_device(ser):
                print("No valid response from device.")
                return
            exit_at_mode(ser)

            print(f"Listening for LoRa messages on {SERIAL_PORT}...\n")
            while True:
                if ser.in_waiting > 0:
                    message = ser.readline().decode('utf-8', errors='replace').strip()
                    if message:
                        print(f"[LoRa Received] {message}")
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nStopped by user.")

if __name__ == "__main__":
    listen_lora()

