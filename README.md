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
