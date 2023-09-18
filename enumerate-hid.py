"""
File: enumerate-hid.py
Author: Chuncheng Zhang
Date: 2023-09-12
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Amazing things

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2023-09-12 ------------------------
# Requirements and constants
import time
import hid
import threading

import pandas as pd

from rich import print, inspect
from IPython.display import display


# %% ---- 2023-09-12 ------------------------
# Function and class

# %% ---- 2023-09-12 ------------------------
# Play ground
hid_devices = hid.enumerate()
print(pd.DataFrame(hid_devices))
# print(hid_devices)


# %% ---- 2023-09-12 ------------------------
# Pending

# lst = []
# for info in hid_devices:
#     path = info['path']

#     device = hid.Device(path=path)
#     # print(info['product_string'], device)

#     out = dict(
#         info,
#         recv='----'
#     )

#     # try:
#     #     # device.write(b'\x01\x80\x33\x01\x00\x00\x00\x00')
#     #     out['recv'] = device.read(1, timeout=100)
#     #     lst.append(out)
#     # except Exception as err:
#     #     out['recv'] = err
#     #     continue

#     print(out)

# display(pd.DataFrame(lst))

# %% ---- 2023-09-12 ------------------------
# Pending

# inspect(device, all=True)

# %%

selected = [e for e in hid_devices
            if e['product_string'] == 'HIDtoUART example'][0]

device = hid.Device(path=selected['path'])

print(selected, device)


def digit2int(buffer17):
    b4 = buffer17[4]
    b3 = buffer17[3]
    decoded = b4 * 256 + b3
    return decoded


class RealTimeHidReader(object):
    sample_rate = 125  # Hz
    running = False

    def __init__(self, device):
        self.device = device
        self.ts = 1 / self.sample_rate  # milliseconds

    def stop(self):
        self.running = False

    def start(self):
        self.buffer = []
        self.n = 0
        t = threading.Thread(target=self.reading, args=(), daemon=True)
        t.start()

    def reading(self):
        self.running = True

        device = self.device

        t0 = time.time()
        while self.running:
            t = time.time()

            if t >= (t0 + self.n * self.ts):
                buffer17 = device.read(17, timeout=100)
                x = digit2int(buffer17)
                self.buffer.append((x, t))
                self.n += 1

                if self.n % self.sample_rate == 0:
                    print(self.n // self.sample_rate, len(self.buffer))


rthr = RealTimeHidReader(device)

rthr.start()

time.sleep(10)

# %%


# for _ in range(1000000):
#     buffer17 = device.read(17, timeout=100)
#     x = digit2int(buffer17)
#     print(_, x, flush=True)
#     time.sleep(0.01)
# %%

# %%


# %%
