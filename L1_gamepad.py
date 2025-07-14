# L1_gamepad.py
import time
import threading
import numpy as np
from evdev import list_devices, InputDevice, ecodes

class Gamepad:
    # raw axis min/max (your sticks) and trigger threshold
    DEADZONE = 125
    TRIGGER_THRESHOLD = 10   # >10 counts as “pressed”
    
    def __init__(self):
        # Get first gamepad (any device that reports analog sticks)
        devices = [InputDevice(d) for d in list_devices()]
        gamepads = [d for d in devices if ecodes.EV_ABS in d.capabilities()]

        self._dev = gamepads[0]
        print("Found gamepad:", self._dev.name)

        # map only the four main axes
        self.axesMap = {
            ecodes.ABS_X:  'LEFT_X',
            ecodes.ABS_Y:  'LEFT_Y',
            ecodes.ABS_RX: 'RIGHT_X',
            ecodes.ABS_RY: 'RIGHT_Y',
        }

        # digital buttons
        self.buttonMap = {
            ecodes.BTN_SOUTH: 'Y',
            ecodes.BTN_EAST:  'B',
            ecodes.BTN_C:     'A',
            ecodes.BTN_NORTH: 'X',
            ecodes.BTN_WEST:  'LB',
            ecodes.BTN_Z:     'RB',
            ecodes.BTN_TL2:   'BACK',
            ecodes.BTN_TR2:   'START',
            ecodes.BTN_SELECT:'L_JOY',
            ecodes.BTN_START: 'R_JOY',
            ecodes.BTN_MODE:  'MODE',
            # note: BTN_TL and BTN_TR are the bumpers, not triggers
            ecodes.BTN_TL:    'LT',   # if your pad reports a digital LT/RT
            ecodes.BTN_TR:    'RT',
        }

        # Ask gamepad for its raw minimum and maximum values for the X and Y axes
        caps = self._dev.capabilities(verbose=True, absinfo=True)
        print("Gamepad capabilities:", caps)

        self.axis_ranges = {}
        for abs_code, logical in self.axesMap.items():
            info = self._dev.absinfo(abs_code)
            self.axis_ranges[logical] = (info.min, info.max, info.flat)
            print(f"{logical}: raw_min={info.min}, raw_max={info.max}, deadzone={info.flat}, threshold={info.fuzz}")

        # initialize everything
        self.axes = {name: None for name in self.axesMap.values()}
        self.buttons = {name: 0 for name in self.buttonMap.values()}
        self.hat = [0, 0]
        self.states = {'axes': self.axes, 'buttons': self.buttons, 'hat': self.hat}

        self.stateUpdating = False
        self.thread = threading.Thread(target=self._updater, daemon=True)
        self.thread.start()

    def _poll(self):
        for event in self._dev.read_loop():
            code, val = event.code, event.value
            name = ecodes.keys[code]

            if event.type == ecodes.EV_ABS:
                # D-pad
                if code in (ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y, ecodes.ABS_HAT1X, ecodes.ABS_HAT1Y, ecodes.ABS_HAT2X, ecodes.ABS_HAT2Y, ecodes.ABS_HAT3X, ecodes.ABS_HAT3Y):
                    if code % 2 == 0:  # X axis
                        self.hat[0] = val
                    else:              # Y axis
                        self.hat[1] = val

                # main analog sticks
                elif code in self.axesMap:
                    mapped_name = self.axesMap[code]
                    self.axes[mapped_name] = val

                # treat analog triggers as digital buttons
                elif code == ecodes.ABS_Z:    # left trigger
                    self.buttons['LT'] = 1 if val > self.TRIGGER_THRESHOLD else 0
                elif code == ecodes.ABS_RZ:   # right trigger
                    self.buttons['RT'] = 1 if val > self.TRIGGER_THRESHOLD else 0

                # anything else: ignore
                else:
                    continue

            elif event.type == ecodes.EV_KEY:
                if code in self.buttonMap:
                    mapped_name = self.buttonMap[code]
                    self.buttons[mapped_name] = val
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

    def readValues(self):
        if not self.stateUpdating:
            return None

        # Unpack raw axis values
        raw_left_x = self.axes['LEFT_X']
        raw_left_y = self.axes['LEFT_Y']
        raw_right_x = self.axes['RIGHT_X']
        raw_right_y = self.axes['RIGHT_Y']
        
        # scale sticks ⇒ [-1, +1]
        # TODO: Verify direction of each axis. Right now, the +Y axis points down
        left_x = self._scaleAxisValue(raw_left_x, *self.axis_ranges['LEFT_X'])
        left_y = self._scaleAxisValue(raw_left_y, *self.axis_ranges['LEFT_Y'])
        right_x = self._scaleAxisValue(raw_right_x, *self.axis_ranges['RIGHT_X'])
        right_y = self._scaleAxisValue(raw_right_y, *self.axis_ranges['RIGHT_Y'])

        axes = [left_x, left_y, right_x, right_y]

        # pack buttons (now including LT/RT from triggers)
        buttons = np.array([
            self.buttons['Y'],   self.buttons['B'],
            self.buttons['A'],   self.buttons['X'],
            self.buttons['LB'],  self.buttons['RB'],
            self.buttons['LT'],  self.buttons['RT'],
            self.buttons['BACK'],self.buttons['START'],
            self.buttons['L_JOY'],self.buttons['R_JOY'],
        ], dtype=int)

        return np.hstack((axes, buttons))
    
    def _scaleAxisValue(self, raw_value: int | None, raw_min: int, raw_max: int, deadzone: int) -> float:
        """Scale a raw axis value to a float in the range [-1.0, 1.0]."""
        if raw_value is None:
            return 0.0

        # Shift raw value to be centered around zero
        raw_cen = (raw_min + raw_max) / 2
        centered_value = raw_value - raw_cen
        
        if abs(centered_value) < deadzone:
            # Within deadzone, treat as zero
            return 0.0

        # Normalize by half of the total range
        raw_span = (raw_max - raw_min) / 2
        return centered_value / raw_span

if __name__ == "__main__":
    gamepad = Gamepad()
    
    while True:
        data = gamepad.readValues()
        if data is None:
            break
        print(data)
        time.sleep(0.05)