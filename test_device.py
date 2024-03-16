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


def digit2int(bytes16: bytes) -> int:
    """Convert 16 bytes buffer into integer

    Args:
        bytes16 (bytes): The input 16 bytes buffer.

    Returns:
        int: The converted integer.
    """
    b4 = bytes16[4]
    b3 = bytes16[3]
    decoded = b4 * 256 + b3
    return decoded


g0 = 44064
g200 = 46122

# %% ---- 2023-11-28 ------------------------
# Play ground
hid_devices = hid.enumerate()

select = None
for device in hid_devices:
    print(device)
    if device["product_string"] == "HIDtoUART example":
        select = device

print("-" * 80)
print(f"Found pressure device: {select}")
print("Reading a data for example:")
device = hid.device()
device.open_path(select["path"])

bytes16 = device.read(16)
value = digit2int(bytes16)
pressure = (value - g0) / (g200 - g0) * 200

print("-" * 80)
print(f"The bytes16 is {bytes16}")
print(f"Decoded value: {value}")
print(f"Pressure (est.): {pressure}")

device.close()
print("Read a data.")

# %% ---- 2023-11-28 ------------------------
# Pending

# %% ---- 2023-11-28 ------------------------
# Pending

# %%

# %%
