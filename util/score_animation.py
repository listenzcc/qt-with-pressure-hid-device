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
import time
import numpy as np

from threading import Thread

from rich import print, inspect
from PIL import Image, ImageDraw, ImageFont

from . import LOGGER


# %% ---- 2023-10-30 ------------------------
# Function and class
def pil2rgb(img):
    mat = np.array(img, dtype=np.uint8)
    # mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
    return mat


class ScoreAnimation(object):
    score_max = 100
    score_min = 0
    score_default = 50
    interval = 100  # ms
    width = 800
    height = 600
    font = ImageFont.truetype(r'C:\\WINDOWS\\FONTS\\MSYHL.TTC',
                              size=width//20)
    img = Image.new(mode='RGB', size=(width, height))
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

    def shift(self):
        img = self.pop()
        if img is not None:
            self.img = img
        return img

    def _animating(self):
        secs = self.interval / 1000
        while self.shift() is not None:
            time.sleep(secs)
        LOGGER.debug('Finished animating')

    def update_score(self, step):
        self.score += step

        self.score = min(self.score, self.score_max)
        self.score = max(self.score, self.score_min)

        LOGGER.debug(f'Updated score {self.score}')

    def mk_frames(self):
        bg = Image.new(mode='RGB', size=(
            self.width, self.height), color='black')
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

        Thread(target=self._animating, daemon=True).start()

    def scale_x(self, x: float) -> int:
        return int(x * self.width)

    def scale_y(self, y: float) -> int:
        return int(y * self.height)

    def scale(self, xy: tuple) -> tuple:
        x, y = xy
        return (self.scale_x(x), self.scale_y(y))

    def tiny_window(self, img, ref=0, pairs=None):
        if pairs is None:
            pairs = [(ref,), (ref,)]

        if len(pairs) == 1:
            pairs.append(pairs[0])

        n = len(pairs)

        img = img.copy()

        x = np.linspace(0.8, 0.9, n)
        z = np.array([e[0] for e in pairs])
        w = np.abs(z-ref) / ref
        y = 0.5 - 0.1 * np.sign(z-ref) * (1-np.exp(-w))
        xy = [self.scale((a, b)) for a, b in zip(x, y)]

        draw = ImageDraw.Draw(img, mode='RGB')

        draw.line([self.scale((0.8, 0.5)), self.scale((0.9, 0.5))], fill='red')
        draw.line(xy, fill='green')

        return img


# %% ---- 2023-10-30 ------------------------
# Play ground


# %% ---- 2023-10-30 ------------------------
# Pending


# %% ---- 2023-10-30 ------------------------
# Pending
