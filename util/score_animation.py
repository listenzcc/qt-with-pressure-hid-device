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

from . import LOGGER, root_path


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
    score = score_default

    interval = 50  # ms, 50 ms refers 20 frames per second
    width = 800
    height = 600

    font = ImageFont.truetype(root_path.joinpath('font/MSYHL.ttc').as_posix(),
                              size=width//20)

    gif = Image.open(root_path.joinpath('img/building.gif'))
    # gif = Image.open(root_path.joinpath('img/giphy.gif'))

    img = Image.new(mode='RGB', size=(width, height))

    buffer = []

    def __init__(self):
        self.gif_buffer = self.parse_gif()
        self.reset()

    def parse_gif(self):
        gif_buffer = []

        n = self.gif.n_frames

        for j in range(100):
            self.gif.seek(int(j/2))
            # self.gif.seek(int(j/10))
            gif_buffer.append(self.gif.convert('RGB'))
        LOGGER.debug('Parsed gif into gif_buffer')
        return gif_buffer

    def reset(self, score: int = None):
        self.score = self.score_default if score is None else score
        self.buffer = []

        LOGGER.debug(f'Score animation is reset, {self.score}, {score}')

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

    def mk_frames(self, score: int = None):
        if score is None:
            score = self.score
            LOGGER.warning(f'Score is not provided, use the current: {score}')

        bg = Image.new(mode='RGB', size=(
            self.width, self.height), color='black')

        step = 1 if self.score < score else -1

        if self.buffer:
            self.buffer = []
            LOGGER.warning(
                'The buffer is not empty, it means the animation is stopped by force')

        for s in range(self.score, score + np.sign(step), step):
            img = self.gif_buffer[s].copy()
            img = img.resize((self.width, self.height))

            draw = ImageDraw.Draw(img, mode='RGB')

            draw.text(
                self.scale((0.5, 0.1)),
                f'-- 得分 {s} | {score} --',
                font=self.font,
                anchor='ms',
                fill='red')

            draw.rectangle(
                (self.scale((0.2, 0.9)), self.scale((0.8, 0.95))), outline='#331139')

            draw.rectangle(
                (self.scale((0.2, 0.9)), self.scale((0.2 + 0.6 * s / 100, 0.95))), fill='#331139')

            self.buffer.append(img)

        self.score = score

        # for j in range(10):
        #     img = bg.copy()
        #     draw = ImageDraw.Draw(img, mode='RGB')

        #     draw.rectangle(
        #         (self.scale((0.1, 0.2)), self.scale((0.5, 0.6))),
        #         fill=(j * 25, 0, 0),
        #         outline='white')

        #     draw.text(self.scale((0.5, 0.3)),
        #               f'-- 序号 {j} --', font=self.font, fill='white')

        #     self.buffer.append(img)
        #     # print(j, self.score, img)

        Thread(target=self._animating, daemon=True).start()

    def scale_x(self, x: float) -> int:
        return int(x * self.width)

    def scale_y(self, y: float) -> int:
        return int(y * self.height)

    def scale(self, xy: tuple) -> tuple:
        x, y = xy
        return (self.scale_x(x), self.scale_y(y))

    def tiny_window(self, img, ref=0, pairs=None):
        '''
        Small window for real-time pressure value vs. reference pressure.

        Draw the curves into the img's clone, so the input img is kept unchanged,
        and the output is the new image with the curves.

        '''
        if pairs is None:
            pairs = [(ref,), (ref,)]

        if len(pairs) == 1:
            pairs.append(pairs[0])

        n = len(pairs)

        img = img.copy()

        left = 0.7
        right = 0.9
        center_height = 0.5
        half_height = 0.2

        x = np.linspace(left, right, n)
        z = np.array([e[0] for e in pairs])
        w = np.abs(z-ref) / ref
        y = center_height - half_height * np.sign(z-ref) * (1-np.exp(-w))
        xy = [self.scale((a, b)) for a, b in zip(x, y)]

        draw = ImageDraw.Draw(img, mode='RGB')

        # Reference curve
        draw.line([
            self.scale((left, center_height)),
            self.scale((right, center_height))
        ], fill='green')

        # Real-time curve
        draw.line(xy, fill='red')

        return img


# %% ---- 2023-10-30 ------------------------
# Play ground


# %% ---- 2023-10-30 ------------------------
# Pending


# %% ---- 2023-10-30 ------------------------
# Pending
