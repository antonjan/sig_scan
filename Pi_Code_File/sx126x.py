# This file is used for LoRa and Raspberry pi4B related issues 

import RPi.GPIO as GPIO
import serial
import time
import atexit  # 👈 Added for cleanup

class sx126x:

    M0 = 22
    M1 = 27
    cfg_reg = [0xC2,0x00,0x09,0x00,0x00,0x00,0x62,0x00,0x12,0x43,0x00,0x00]
    get_reg = bytes(12)
    rssi = False
    addr = 65535
    serial_n = ""
    addr_temp = 0

    start_freq = 850
    offset_freq = 18

    SX126X_UART_BAUDRATE_1200 = 0x00
    SX126X_UART_BAUDRATE_2400 = 0x20
    SX126X_UART_BAUDRATE_4800 = 0x40
    SX126X_UART_BAUDRATE_9600 = 0x60
    SX126X_UART_BAUDRATE_19200 = 0x80
    SX126X_UART_BAUDRATE_38400 = 0xA0
    SX126X_UART_BAUDRATE_57600 = 0xC0
    SX126X_UART_BAUDRATE_115200 = 0xE0

    SX126X_PACKAGE_SIZE_240_BYTE = 0x00
    SX126X_PACKAGE_SIZE_128_BYTE = 0x40
    SX126X_PACKAGE_SIZE_64_BYTE = 0x80
    SX126X_PACKAGE_SIZE_32_BYTE = 0xC0

    SX126X_Power_22dBm = 0x00
    SX126X_Power_17dBm = 0x01
    SX126X_Power_13dBm = 0x02
    SX126X_Power_10dBm = 0x03

    lora_air_speed_dic = {
        1200: 0x01,
        2400: 0x02,
        4800: 0x03,
        9600: 0x04,
        19200: 0x05,
        38400: 0x06,
        62500: 0x07
    }

    lora_power_dic = {
        22: 0x00,
        17: 0x01,
        13: 0x02,
        10: 0x03
    }

    lora_buffer_size_dic = {
        240: SX126X_PACKAGE_SIZE_240_BYTE,
        128: SX126X_PACKAGE_SIZE_128_BYTE,
        64: SX126X_PACKAGE_SIZE_64_BYTE,
        32: SX126X_PACKAGE_SIZE_32_BYTE
    }

    def __init__(self, serial_num, freq, addr, power, rssi, air_speed=2400,
                 net_id=0, buffer_size=240, crypt=0,
                 relay=False, lbt=False, wor=False):
        self.rssi = rssi
        self.addr = addr
        self.freq = freq
        self.serial_n = serial_num
        self.power = power

        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.M0, GPIO.OUT)
        GPIO.setup(self.M1, GPIO.OUT)
        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)

        self.ser = serial.Serial(serial_num, 9600)
        self.ser.flushInput()
        self.set(freq, addr, power, rssi, air_speed, net_id, buffer_size, crypt, relay, lbt, wor)

    def set(self, freq, addr, power, rssi, air_speed=2400,
            net_id=0, buffer_size=240, crypt=0,
            relay=False, lbt=False, wor=False):
        self.send_to = addr
        self.addr = addr

        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)

        low_addr = addr & 0xff
        high_addr = addr >> 8 & 0xff
        net_id_temp = net_id & 0xff

        if freq > 850:
            freq_temp = freq - 850
            self.start_freq = 850
            self.offset_freq = freq_temp
        elif freq > 410:
            freq_temp = freq - 410
            self.start_freq = 410
            self.offset_freq = freq_temp

        air_speed_temp = self.lora_air_speed_dic.get(air_speed, None)
        buffer_size_temp = self.lora_buffer_size_dic.get(buffer_size, None)
        power_temp = self.lora_power_dic.get(power, None)

        rssi_temp = 0x80 if rssi else 0x00
        l_crypt = crypt & 0xff
        h_crypt = crypt >> 8 & 0xff

        if not relay:
            self.cfg_reg[3] = high_addr
            self.cfg_reg[4] = low_addr
            self.cfg_reg[5] = net_id_temp
            self.cfg_reg[6] = self.SX126X_UART_BAUDRATE_9600 + air_speed_temp
            self.cfg_reg[7] = buffer_size_temp + power_temp + 0x20
            self.cfg_reg[8] = freq_temp
            self.cfg_reg[9] = 0x43 + rssi_temp
            self.cfg_reg[10] = h_crypt
            self.cfg_reg[11] = l_crypt
        else:
            self.cfg_reg[3] = 0x01
            self.cfg_reg[4] = 0x02
            self.cfg_reg[5] = 0x03
            self.cfg_reg[6] = self.SX126X_UART_BAUDRATE_9600 + air_speed_temp
            self.cfg_reg[7] = buffer_size_temp + power_temp + 0x20
            self.cfg_reg[8] = freq_temp
            self.cfg_reg[9] = 0x03 + rssi_temp
            self.cfg_reg[10] = h_crypt
            self.cfg_reg[11] = l_crypt

        self.ser.flushInput()

        for i in range(2):
            self.ser.write(bytes(self.cfg_reg))
            time.sleep(0.2)
            if self.ser.inWaiting() > 0:
                time.sleep(0.1)
                r_buff = self.ser.read(self.ser.inWaiting())
                if r_buff[0] == 0xC1:
                    break
            else:
                print("setting fail,setting again")
                self.ser.flushInput()
                time.sleep(0.2)
                if i == 1:
                    print("setting fail,Press Esc to Exit and run again")

        GPIO.output(self.M0, GPIO.LOW)
        GPIO.output(self.M1, GPIO.LOW)
        time.sleep(0.1)

    def get_settings(self):
        GPIO.output(self.M1, GPIO.HIGH)
        time.sleep(0.1)

        self.ser.write(bytes([0xC1, 0x00, 0x09]))
        if self.ser.inWaiting() > 0:
            time.sleep(0.1)
            self.get_reg = self.ser.read(self.ser.inWaiting())

        if self.get_reg[0] == 0xC1 and self.get_reg[2] == 0x09:
            fre_temp = self.get_reg[8]
            addr_temp = self.get_reg[3] + self.get_reg[4]
            air_speed_temp = self.get_reg[6] & 0x03
            power_temp = self.get_reg[7] & 0x03

            print("Frequence is {0}.125MHz.".format(fre_temp))
            print("Node address is {0}.".format(addr_temp))
            print("Air speed is {0} bps".format(self.lora_air_speed_dic.get(None, air_speed_temp)))
            print("Power is {0} dBm".format(self.lora_power_dic.get(None, power_temp)))

            GPIO.output(self.M1, GPIO.LOW)

    def send(self, data):
        GPIO.output(self.M1, GPIO.LOW)
        GPIO.output(self.M0, GPIO.LOW)
        time.sleep(0.1)
        self.ser.write(data)
        time.sleep(0.1)

    def receive(self):
        if self.ser.inWaiting() > 0:
            time.sleep(0.5)
            r_buff = self.ser.read(self.ser.inWaiting())

            print("receive message from node address with frequence\033[1;32m %d,%d.125MHz\033[0m" % (
                (r_buff[0] << 8) + r_buff[1], r_buff[2] + self.start_freq))
            print("message is " + str(r_buff[3:-1]))

            if self.rssi:
                print("the packet rssi value: -{0}dBm".format(256 - r_buff[-1:][0]))
                self.get_channel_rssi()

    def get_channel_rssi(self):
        GPIO.output(self.M1, GPIO.LOW)
        GPIO.output(self.M0, GPIO.LOW)
        time.sleep(0.1)
        self.ser.flushInput()
        self.ser.write(bytes([0xC0, 0xC1, 0xC2, 0xC3, 0x00, 0x02]))
        time.sleep(0.5)
        re_temp = bytes(5)
        if self.ser.inWaiting() > 0:
            time.sleep(0.1)
            re_temp = self.ser.read(self.ser.inWaiting())
        if re_temp[0] == 0xC1 and re_temp[1] == 0x00 and re_temp[2] == 0x02:
            print("the current noise rssi value: -{0}dBm".format(256 - re_temp[3]))
        else:
            print("receive rssi value fail")

# ✅ Added GPIO cleanup at exit
atexit.register(GPIO.cleanup)

