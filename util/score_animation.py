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
import numpy as np

from threading import Thread
from PIL import Image, ImageDraw

from tqdm.auto import tqdm

from . import logger, root_path
from .automatic_animation import AutomaticAnimation


# %% ---- 2023-10-30 ------------------------
# Function and class
def pil2rgb(img):
    mat = np.array(img, dtype=np.uint8)
    # mat = cv2.cvtColor(mat, cv2.COLOR_BGR2RGB)
    return mat


class ScoreAnimation(AutomaticAnimation):
    '''
    The pipeline of the animation is append the self.buffer using images.
    The self.gif_buffer store the animation images.
    '''

    # ? --------------------------------------------------------------------------------
    # ? Potential problem:
    # ? It causes image blinking as the resolution is changed,
    # ? since the images had been created using the previous resolution.
    # ? --------------------------------------------------------------------------------

    score_max = 100
    score_min = 0
    score_default = 50
    score = score_default

    resource_OK = False

    gif = Image.open(root_path.joinpath('img/building.gif'))
    # gif = Image.open(root_path.joinpath('img/giphy.gif'))

    def __init__(self):
        super(ScoreAnimation, self).__init__()
        try:
            self.gif_buffer = self.parse_gif()
            self.resource_OK = True
            logger.info('Loaded required resource')
        except Exception as err:
            self.resource_traceback = f'{err}'
            logger.error('Failed loading required resources')

        self.reset()

    def parse_gif(self):
        gif_buffer = []

        n = self.gif.n_frames

        for j in tqdm(range(100), 'Loading gif'):
            self.gif.seek(int(j/2)+1)
            # self.gif.seek(int(j/10))
            gif_buffer.append(self.gif.convert('RGB'))
        logger.debug('Parsed gif into gif_buffer')

        return gif_buffer

    def reset(self, score: int = None):
        """
        Resets the score animation by setting the score to the default value and clearing the buffer.

        Args:
            self: The ScoreAnimation instance.
            score (int, optional): The new score value. If not provided, the default score value will be used.

        Returns:
            int: The updated score value.

        Examples:
            anim = ScoreAnimation()
            anim.reset()
            anim.reset(100)
        """

        self.score = self.score_default if score is None else score
        self.fifo_buffer = []

        logger.debug(f'Score animation is reset, {self.score}, {score}')

        return self.score

    def pop_all(self):
        frames = list(self.fifo_buffer)
        self.fifo_buffer = []
        return frames

    def safe_update_score(self, step):
        score = self.score + step

        score = min(score, self.score_max)
        score = max(score, self.score_min)

        return score

    def mk_frames(self, score: int = None):
        if score is None:
            score = self.score
            logger.warning(f'Score is not provided, use the current: {score}')

        # bg = Image.new(mode='RGB', size=(
        #     self.width, self.height), color='black')

        step = 1 if self.score < score else -1

        if self.fifo_buffer:
            self.fifo_buffer = []
            logger.warning(
                'The buffer is not empty, it means the animation is stopped by force')

        for s in range(self.score, score + np.sign(step), step):
            img = self.gif_buffer[s].copy()
            img = img.resize((self.width, self.height))

            # Make the drawer as draw
            draw = ImageDraw.Draw(img, mode='RGB')

            # Draw the score text
            draw.text(
                self.scale((0.5, 0.1)),
                f'-- 得分 {s} | {score} --',
                font=self.font,
                anchor='ms',
                fill='red')

            # Draw the score bar's background
            draw.rectangle(
                (self.scale((0.2, 0.9)), self.scale((0.8, 0.95))), outline='#331139')

            # Draw the score bar's foreground
            draw.rectangle(
                (self.scale((0.2, 0.9)), self.scale((0.2 + 0.6 * s / 100, 0.95))), fill='#331139')

            # Append to the buffer
            self.fifo_buffer.append(img)

        self.score = score

        Thread(target=self.animating_loop, daemon=True).start()

    def scale(self, xy: tuple) -> tuple:
        return self.scale_xy_ratio(xy)


# %% ---- 2023-10-30 ------------------------
# Play ground


# %% ---- 2023-10-30 ------------------------
# Pending


# %% ---- 2023-10-30 ------------------------
# Pending
