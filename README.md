# sig_scan
This project will scan for rf signals and report them if there is signals detected using an rtl-sdr dongle on a a Raspberry Pi<br>
Libraery with exsyended frequency is avalable here https://github.com/librtlsdr/librtlsdr/tree/development<br>
## Pre Req libraeriies
    sudo apt-get install build-essential cmake git
    sudo apt-get install libusb-dev libusb-1.0-0-dev
    git clone https://github.com/librtlsdr/librtlsdr/tree/development
    cd librtlsdr
    git checkout development
    git status

    mkdir build && cd build
    cmake ../ -DINSTALL_UDEV_RULES=ON
    make

    sudo make install
    sudo ldconfig
# Setting up python 
    cd Documents/SX126X_LoRa_HAT_Code/raspberrypi/python/
## Sender 
    source ~/sdr-env/bin/activate
## Receiver
    source venv/bin/activate
# Running SIG Scanner
python gsm_scanner_new2.py

# Rafial R828D pin conections

    R828D (R820T-compatible) Pinout: Pin Number to Name

The R828D is usually supplied in a 32-pin QFN package. Here’s the most commonly reported pinout:

        Pin	Name	Function
        1	VCC	Power supply
        2	VCO	PLL VCO
        3	VCOIN	PLL VCO input
        4	VCOGND	PLL VCO ground
        5	VCOBUF	PLL VCO buffer output
        6	XIN	Crystal oscillator input
        7	XOUT	Crystal oscillator out
        8	VCC	Power supply
        9	GND	Ground
        10	AGC	Automatic Gain Control
        11	IFOUT	Intermediate Frequency Output
        12	VCC	Power supply
        13	GND	Ground
        14	RF_IN	RF Input (from antenna)
        15	GND	Ground
        16	NC	Not Connected
        17	VCC	Power supply
        18	NC	Not Connected
        19	LNA	Low Noise Amp control
        20	VCC	Power supply
        21	GND	Ground
        22	NC	Not Connected
        23	SDA	I²C Data
        24	SCL	I²C Clock
        25	GND	Ground
        26	VCC	Power supply
        27	NC	Not Connected
        28	VCC	Power supply
        29	NC	Not Connected
        30	NC	Not Connected
        31	NC	Not Connected
        32	NC	Not Connected
        30	NC	Not Connected
        31	NC	Not Connected
        32	NC	Not Connected
## Basic Connections

    Antenna → Matching Network → Pin 14 (RF_IN)
    Pin 11 (IFOUT) → RTL2832U IF Input
    Pin 23 (SDA) & Pin 24 (SCL) → RTL2832U I²C (for control)
    Pin 6 (XIN) & Pin 7 (XOUT) → 16 MHz Crystal (one end to XIN, other to XOUT, with load capacitors to GND)
    All VCC Pins → 3.3V Power
    All GND Pins → Ground Plane

## Register Map (Community Reference, RTL-SDR Driver)

The R828D is controlled via I²C. The register map is not openly published, but the rtl-sdr driver configures it as follows:

    I²C Address: 0x8C (write), 0x8D (read)
    Registers:
        Reg 0x00: Tuner enable, AGC, LNA setting
        Reg 0x01–0x05: PLL and frequency control
        Reg 0x06–0x0D: IF settings, filter bandwidth, gain stages
        Reg 0x0E–0x1F: Misc control, calibration, test modes

Example I²C Write Sequence for Initialization:
    
    uint8_t init_regs[] = {
    0x01, 0x16, 0xE0, 0x60, 0x40, // PLL settings
    0x20, 0x80, 0x40,             // IF gain, filter
    0xA1, 0x4B, 0x10              // AGC, LNA, etc.
    };
    i2c_write(R828D_ADDR, init_regs, sizeof(init_regs));
The actual values depend on frequency, IF, and gain requirements.
Refer to rtl-sdr tuner_r820t.c for full register programming examples. https://github.com/osmocom/rtl-sdr/blob/master/src/tuner_r820t.c

Step-by-Step Build Guide

    Connect RF_IN (Pin 14) to antenna/matching network.
    Connect IFOUT (Pin 11) to RTL2832U IF Input.
    Connect SDA (Pin 23) and SCL (Pin 24) to RTL2832U I²C bus. Use pull-up resistors (~4.7kΩ) to 3.3V.
    Connect 16 MHz crystal between XIN (Pin 6) and XOUT (Pin 7), with recommended load capacitors (~22pF) to ground.
    Connect all VCC pins to regulated 3.3V supply.
    Connect all GND pins to system ground.
    AGC (Pin 10) and LNA (Pin 19) can be controlled by RTL2832U or tied appropriately.
    Initialize R828D via I²C using register sequences from open-source drivers.
# R828 c driver 
https://github.com/osmocom/rtl-sdr/blob/master/src/tuner_r82xx.c

    
    Pin 10 (AGC) → RTL2832U AGC Output (optional, for gain control)
    Pin 19 (LNA) → Can be tied HIGH or controlled by RTL2832U for LNA operation
