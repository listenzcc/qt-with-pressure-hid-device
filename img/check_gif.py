"""
File: check_gif.py
Author: Chuncheng Zhang
Date: 2023-11-03
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


# %% ---- 2023-11-03 ------------------------
# Requirements and constants
import numpy as np

from PIL import Image
from pathlib import Path

from rich import print, inspect


# %% ---- 2023-11-03 ------------------------
# Function and class
root = Path(__file__).parent
gif = root.joinpath('building.gif')
gif = root.joinpath('giphy.gif')
gif

# %% ---- 2023-11-03 ------------------------
# Play ground
img = Image.open(gif)
inspect(img)
print(np.array(img).shape)
img


# %% ---- 2023-11-03 ------------------------
# Pending
img.seek(60)
display(img)
np.array(img)


# %% ---- 2023-11-03 ------------------------
# Pending
