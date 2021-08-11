#!/usr/bin/env python3

import subprocess
import threading
import time

try:
    import uinput
except ImportError:
    raise SystemExit('uinput module missing -- to install run "sudo apt install python3-uinput"')

try:
    import RPi.GPIO as GPIO
except ImportError:
    raise SystemExit('RPi.GPIO module missing -- to install run "sudo apt install rpi.gpio"')


# this is the mapping of GPIO numbers (in BCM mode) to key codes
CHANNELS = {
    6: uinput.KEY_UP,
    13: uinput.KEY_DOWN,
    19: uinput.KEY_LEFT,
    26: uinput.KEY_RIGHT,
    20: uinput.KEY_LEFTCTRL,  # button A
    21: uinput.KEY_LEFTALT,  # button B
}

KEYS = list(CHANNELS.values())

# Debounce time in seconds
BOUNCETIME = 1.0 / 100


def capture_keys():
    GPIO.setmode(GPIO.BCM)

    with uinput.Device(KEYS, name="amiga-joystick") as device:
        # current state of all buttons
        state = {ch: False for ch in CHANNELS}

        condition = threading.Condition()
        inputs_changed = set()

        # this will get called when the Raspberry detects a change on the
        # inputs
        def callback(channel):
            with condition:
                inputs_changed.add(channel)
                condition.notify()

        # setup GPIOs and callbacks
        for channel in CHANNELS:
            GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.add_event_detect(channel, GPIO.BOTH, callback=callback)

        # all set, start looping
        while True:
            with condition:
                # wait for at least one input to change
                while not inputs_changed:
                    condition.wait()

                # process the changes
                while inputs_changed:
                    channel = inputs_changed.pop()
                    ch_state = not GPIO.input(channel)
                    if state[channel] != ch_state:
                        # a button got pressed or released
                        state[channel] = ch_state
                        device.emit(CHANNELS[channel], ch_state)

            # take a short break to do a kind of debouncing
            time.sleep(BOUNCETIME)


def main():
    # run the function in a separate background thread -- otherwise it's not
    # possible to interrupt it using CTRL-C
    thread = threading.Thread(target=capture_keys)
    thread.daemon = True
    thread.start()
    # wait forever
    while True:
        input()


if __name__ == "__main__":
    try:
        subprocess.check_call(["modprobe", "uinput"])
        main()
    except KeyboardInterrupt:
        raise SystemExit
