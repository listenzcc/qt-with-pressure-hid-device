"""
File: test_device.py
Author: Chuncheng Zhang
Date: 2023-11-28
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


# %% ---- 2023-11-28 ------------------------
# Requirements and constants
import hid
from rich import print, inspect

# %% ---- 2023-11-28 ------------------------
# Function and class


# %% ---- 2023-11-28 ------------------------
# Play ground
hid_devices = hid.enumerate()

select = None
for device in hid_devices:
    print(device)
    if device['product_string'] == 'HIDtoUART example':
        select = device

print('-' * 80)
print(f'Found pressure device: {select}')
print('Reading a data for example:')
device = hid.device()
device.open_path(select['path'])
print(device.read(16))
device.close()
print('Read a data.')

# %% ---- 2023-11-28 ------------------------
# Pending

# %% ---- 2023-11-28 ------------------------
# Pending

# %%

# %%
