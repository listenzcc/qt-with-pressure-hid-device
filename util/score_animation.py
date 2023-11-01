"""
File: score_animation.py
Author: Chuncheng Zhang
Date: 2023-10-30
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


# %% ---- 2023-10-30 ------------------------
# Requirements and constants
import cv2
import numpy as np

from rich import print, inspect
from PIL import Image, ImageDraw, ImageFont

from . import LOGGER


# %% ---- 2023-10-30 ------------------------
# Function and class
def pil2rgb(img):
    mat = np.array(img, dtype=np.uint8)
    # mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
    print(mat.shape)
    return mat


class ScoreAnimation(object):
    score_max = 100
    score_min = 0
    score_default = 50
    width = 400
    height = 300
    font = ImageFont.truetype(
        r'C:\\WINDOWS\\FONTS\\MSYHL.TTC', size=int(width/20))

    buffer = []

    def __init__(self):
        self.reset()

    def reset(self, score: int = None):
        self.score = self.score_default if score is None else score
        self.buffer = []

        LOGGER.debug(f'Score animation is reset, {self.score}')

        return self.score

    def pop_all(self):
        frames = list(self.buffer)
        self.buffer = []
        return frames

    def pop(self):
        if len(self.buffer) > 0:
            return self.buffer.pop(0)
        return

    def update(self, step):
        self.score += step

        self.score = min(self.score, self.score_max)
        self.score = max(self.score, self.score_min)

        LOGGER.debug(f'Updated score {self.score}')

    def mk_frames(self):
        bg = Image.new(mode='RGB', size=(self.width, self.height))
        for j in range(10):
            img = bg.copy()
            draw = ImageDraw.Draw(img, mode='RGB')

            draw.rectangle(
                (self.scale((0.1, 0.2)), self.scale((0.5, 0.6))),
                fill=(j * 25, 0, 0),
                outline='white')

            draw.text(self.scale((0.5, 0.3)),
                      f'-- 序号 {j} --', font=self.font, fill='white')

            self.buffer.append(img)
            # print(j, self.score, img)

    def scale_x(self, x: float) -> int:
        return int(x * self.width)

    def scale_y(self, y: float) -> int:
        return int(y * self.height)

    def scale(self, xy: tuple) -> tuple:
        x, y = xy
        return (self.scale_x(x), self.scale_x(y))

# %% ---- 2023-10-30 ------------------------
# Play ground


# %% ---- 2023-10-30 ------------------------
# Pending


# %% ---- 2023-10-30 ------------------------
# Pending
