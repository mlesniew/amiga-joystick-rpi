#!/usr/bin/env bash

if [ "$EUID" -ne 0 ]
then
    echo "Please run this script as root."
    exit 1
fi

set -ex

apt update
apt install -yq rpi.gpio python3-uinput

curl -s -o /usr/local/bin/amiga-joystick.py https://raw.githubusercontent.com/mlesniew/amiga-joystick-rpi/master/amiga-joystick.py
chmod +x /usr/local/bin/amiga-joystick.py

curl -o /etc/systemd/system/amiga-joystick.service https://raw.githubusercontent.com/mlesniew/amiga-joystick-rpi/master/amiga-joystick.service
systemctl daemon-reload
systemctl enable amiga-joystick
systemctl start amiga-joystick
