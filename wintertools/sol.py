# Copyright (c) 2021 Alethea Katherine Flowers.
# Published under the standard MIT License.
# Full text available at: https://opensource.org/licenses/MIT

"""Control Sol to output high-resolution voltage references for calibration."""

import importlib.resources
import struct
import time

from wintertools import midi, fs, log


class Sol(midi.MIDIDevice):
    MIDI_PORT_OUT_NAME = "Sol usb_midi.ports[0]"
    MIDI_PORT_IN_NAME = "Sol usb_midi.ports[1]"
    SYSEX_MARKER = 0x78

    # TODO: Use the USB PID to unique identify the drive in case there are
    # multiple CircuitPython devices connected.
    DRIVE_NAME = "CIRCUITPY"

    def __init__(self):
        super().__init__()

    def setup(self):
        log.info("Copying script to Sol")
        drive = fs.find_drive_by_name("CIRCUITPY")

        with importlib.resources.path(
            "wintertools.data", "sol_circuitpython_code.py"
        ) as src:
            fs.copyfile(src, f"{drive}/main.py")

        # Wait for sol to reboot
        log.info("Waiting for sol to reboot...")
        time.sleep(3)

    def set_voltage(self, voltage, channel=0):
        packed = struct.pack("f", voltage)
        encoded = bytearray(
            [
                (packed[0] >> 4) & 0xF,
                packed[0] & 0xF,
                (packed[1] >> 4) & 0xF,
                packed[1] & 0xF,
                (packed[2] >> 4) & 0xF,
                packed[2] & 0xF,
                (packed[3] >> 4) & 0xF,
                packed[3] & 0xF,
            ]
        )

        self.sysex(0x01, data=[channel] + list(encoded), response=True)
