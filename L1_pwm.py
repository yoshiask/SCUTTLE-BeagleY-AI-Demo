# Based onhttps://github.com/brgl/libgpiod/blob/e4427590d9d63a7104dd5df564dd6b7b0c784547/bindings/python/examples/find_line_by_name.py

import gpiod
import os
from periphery import PWM


def generate_gpio_chips():
    for entry in os.scandir("/dev/"):
        if gpiod.is_gpiochip_device(entry.path):
            yield entry.path


def PWM_by_name(line_name: str) -> PWM:
    # Names are not guaranteed unique, so this finds the first line with
    # the given name.
    for path in generate_gpio_chips():
        with gpiod.Chip(path) as chip:
            try:
                offset = chip.line_offset_from_id(line_name)
                print("{}: {} {}".format(line_name, chip.get_info().name, offset))
                return
            except OSError:
                # An OSError is raised if the name is not found.
                continue
