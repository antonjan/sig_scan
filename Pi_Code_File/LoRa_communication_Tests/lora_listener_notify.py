import serial
import subprocess

def show_notification(title, message):
    subprocess.run(["notify-send", title, message])

def main():
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Adjust baud rate if needed
    print("Listening for LoRa messages on /dev/ttyACM0...")

    while True:
        try:
            line = ser.readline().decode().strip()
            if "ALERT" in line:
                print(f"Received: {line}")
                show_notification("LoRa Alert", line)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()

