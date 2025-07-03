import os
import re
from pathlib import PurePath
from periphery import PWM

_trailing_num_re = re.compile(r"\d+$")

def pwm_chip_from_gpio_pin(gpio_pin: int) -> tuple[int, int]:
    """
    Returns the hardware PWM chip and channel numbers for the requested GPIO pin.
    """
    hat_path = f"/dev/hat/pwm/GPIO{gpio_pin}"

    # Check if the friendly mapping already exists
    if not os.path.isdir(hat_path) or os.readlink(hat_path) == None:
        # Use beagle-pwm-export to map the chip/channel path
        # to a known friendly name
        print(f"Mapping GPIO{gpio_pin} to PWM chip... (sudo required)")
        
        # It seems the symlinks break after the script ends, so we'll
        # want to clean things up before we set it up again
        command = f"sudo rm {hat_path}"
        os.system(command)
        
        command = f"sudo beagle-pwm-export --pin gpio{gpio_pin}"
        exit_code = os.system(command)
        if exit_code != 0:
            raise KeyError()
    
    # Pull the chip and channel numbers from the symlinked path
    target_path = PurePath(os.readlink(hat_path))
    chip_part, channel_part = target_path.parts[-2:]

    chip_num = int(_trailing_num_re.search(chip_part).group())
    channel_num = int(_trailing_num_re.search(channel_part).group())

    return chip_num, channel_num


def pwm_from_gpio_pin(gpio_pin: int) -> PWM:
    """
    Returns a Perhiphery PWM instance for the requested GPIO pin.
    """
    chip_num, channel_num = pwm_chip_from_gpio_pin(gpio_pin)
    return PWM(chip_num, channel_num)


if __name__ == "__main__":
    gpio_pin = int(input("GPIO pin to map: "))
    chip_num, channel_num = pwm_chip_from_gpio_pin(gpio_pin)
    print(f"GPIO{gpio_pin} is on PWM chip {chip_num}, channel {channel_num}")
