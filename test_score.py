"""
File: test_score.py
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
from util.score_animation import ScoreAnimation, pil2rgb


# %% ---- 2023-10-30 ------------------------
# Function and class
wname = 'window'

sa = ScoreAnimation()
sa.reset()


def display():
    frames = sa.pop_all()
    for img in frames:
        mat = np.array(img, dtype=np.uint8)  # .transpose([2, 1, 0])
        mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
        cv2.imshow(wname, mat)
        cv2.waitKey(100)
    return


# %% ---- 2023-10-30 ------------------------
# Play ground

if __name__ == '__main__':
    while True:
        inp = input('>>')

        if inp == 'q':
            break

        sa.mk_frames()

        frames = sa.pop_all()
        n = len(frames)
        tic = time.time()
        for img in frames:
            mat = pil2rgb(img)
            cv2.imshow(wname, mat)
            cv2.waitKey(100)
        t = time.time() - tic
        print(f'{t:.2f}, {t / n:.2f}')

        # t = Thread(target=display, daemon=True)
        # t.start()


# %% ---- 2023-10-30 ------------------------
# Pending


# %% ---- 2023-10-30 ------------------------
# Pending
