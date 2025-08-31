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
    Pin 10 (AGC) → RTL2832U AGC Output (optional, for gain control)
    Pin 19 (LNA) → Can be tied HIGH or controlled by RTL2832U for LNA operation
