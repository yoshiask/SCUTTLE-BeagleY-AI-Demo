# L1_gamepad.py
import time
import threading
import numpy as np
import inputs
from inputs import devices, get_gamepad

# raw axis min/max (your sticks) and trigger threshold
RAW_MIN = 0
RAW_MAX = 255
TRIGGER_THRESHOLD = 10   # >10 counts as “pressed”

class Gamepad:
    def __init__(self):
        gamepads = [d.name for d in devices if isinstance(d, inputs.GamePad)]
        if not gamepads:
            print("\nNo gamepad detected.\n")
            return
        print("Found gamepad(s):", gamepads)
        if 'ESM-9013' not in gamepads:
            print('\nGamepad in incorrect mode.\n')

        # map only the four main axes
        self.axesMap = {
            'ABS_X':  'LEFT_X',
            'ABS_Y':  'LEFT_Y',
            'ABS_RX': 'RIGHT_X',
            'ABS_RY': 'RIGHT_Y',
        }

        # digital buttons
        self.buttonMap = {
            'BTN_SOUTH':'Y',
            'BTN_EAST':  'B',
            'BTN_C':     'A',
            'BTN_NORTH': 'X',
            'BTN_WEST':  'LB',
            'BTN_Z':     'RB',
            'BTN_TL2':   'BACK',
            'BTN_TR2':   'START',
            'BTN_SELECT':'L_JOY',
            'BTN_START': 'R_JOY',
            'BTN_MODE':  'MODE',
            # note: BTN_TL and BTN_TR are the bumpers, not triggers
            'BTN_TL':    'LT',   # if your pad reports a digital LT/RT
            'BTN_TR':    'RT',
        }

        # initialize everything
        self.axes = {name: (RAW_MAX+RAW_MIN)//2 for name in self.axesMap.values()}
        self.buttons = {name: 0 for name in self.buttonMap.values()}
        self.hat = [0, 0]
        self.states = {'axes': self.axes, 'buttons': self.buttons, 'hat': self.hat}

        self.stateUpdating = False
        self.thread = threading.Thread(target=self._updater, daemon=True)
        self.thread.start()

    def _poll(self):
        for event in get_gamepad():
            code, val = event.code, event.state

            if event.ev_type == "Absolute":
                # D-pad
                if code.startswith("ABS_HAT"):
                    if code.endswith("X"):
                        self.hat[0] = val
                    else:
                        self.hat[1] = val

                # main analog sticks
                elif code in self.axesMap:
                    self.axes[self.axesMap[code]] = val

                # treat analog triggers as digital buttons
                elif code == 'ABS_Z':    # left trigger
                    self.buttons['LT'] = 1 if val > TRIGGER_THRESHOLD else 0
                elif code == 'ABS_RZ':   # right trigger
                    self.buttons['RT'] = 1 if val > TRIGGER_THRESHOLD else 0

                # anything else: ignore
                else:
                    continue

            elif event.ev_type == "Key":
                if code in self.buttonMap:
                    self.buttons[self.buttonMap[code]] = val
                else:
                    # unknown key event
                    continue

        # update combined state
        self.states = {'axes': self.axes, 'buttons': self.buttons, 'hat': self.hat}

    def _updater(self):
        self.stateUpdating = True
        try:
            while True:
                self._poll()
        except Exception as e:
            print("Gamepad thread stopped:", e)
            self.stateUpdating = False

    def getStates(self):
        return self.states


def getGP():
    if not gamepad.stateUpdating:
        return None

    # scale sticks ⇒ [-1, +1]
    raw = np.array([
        gamepad.axes['LEFT_X'],
        gamepad.axes['LEFT_Y'],
        gamepad.axes['RIGHT_X'],
        gamepad.axes['RIGHT_Y']
    ], dtype=float)
    axes = (raw - RAW_MIN)/(RAW_MAX-RAW_MIN)*2.0 - 1.0
    axes = np.clip(axes, -1.0, 1.0)

    # pack buttons (now including LT/RT from triggers)
    buttons = np.array([
        gamepad.buttons['Y'],   gamepad.buttons['B'],
        gamepad.buttons['A'],   gamepad.buttons['X'],
        gamepad.buttons['LB'],  gamepad.buttons['RB'],
        gamepad.buttons['LT'],  gamepad.buttons['RT'],
        gamepad.buttons['BACK'],gamepad.buttons['START'],
        gamepad.buttons['L_JOY'],gamepad.buttons['R_JOY'],
    ], dtype=int)

    return np.hstack((axes, buttons))


# instantiate on import so getGP() will always see it
gamepad = Gamepad()

if __name__ == "__main__":
    while True:
        data = getGP()
        if data is None:
            break
        print(data)
        time.sleep(0.05)