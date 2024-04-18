"""
File: two_steps_score_animation.py
Author: Chuncheng Zhang
Date: 2024-04-17
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    The scorer is a two-steps scorer.
    - The 1st step determines if the mean value of the latest pressure values meet the reference;
        - If the mean value satisfies, enter into the 2nd step;
    - In the 2nd step, the standard value of the latest pressure values are calculated controlling the score;
        - If the standard value is lower than a threshold, increase the score;
        - If the standard value is higher than a threshold, decrease the score.

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-04-17 ------------------------
# Requirements and constants
import contextlib
import time
import numpy as np

from PIL import Image, ImageDraw, ImageFont
from threading import Thread
from typing import Any
from tqdm.auto import tqdm

from . import logger, project_conf, root_path


# %% ---- 2024-04-17 ------------------------
# Function and class

# --------------------------------------------------------------------------------
class TwoStepScorer(object):
    mean_ref_value = project_conf['display']['ref_value']
    mean_threshold = project_conf['display']['two_step_animation_mean_threshold']
    std_threshold = project_conf['display']['two_step_animation_std_threshold']
    window_length = project_conf['display']['two_step_animation_window_length']

    state = '1st'
    score_1st_step = 0
    score_2nd_step = 0

    def __init__(self):
        self.reset()
        logger.info("Initialized TwoStepScorer")

    def reset(self):
        self.state = '1st'
        self.score_1st_step = 0
        self.score_2nd_step = 0
        logger.debug('Reset the TwoStepScorer')

    def get_current_state(self):
        return dict(
            state=self.state,
            score_1st=self.score_1st_step,
            score_2nd=self.score_2nd_step,
        )

    def _limit_scores(self):
        '''Keep the scores inside the range of [0, 100]'''
        self.score_1st_step = min(100, max(0, self.score_1st_step))
        self.score_2nd_step = min(100, max(0, self.score_2nd_step))

    def _update_score(self, data: Any):
        # --------------------
        # Current state is 1st
        # Update it with mean value
        if self.state == '1st':
            # Update the score
            mean = np.mean(data)
            diff = np.abs(mean - self.mean_ref_value)
            # Update rule:
            # It is basically the linear rule, but never
            # diff=  0 -> score=100
            # diff=100 -> score=0
            score = 100 - diff
            self.score_1st_step = score
            self._limit_scores()

            # The mean value meets the threshold, enter into the 2nd step
            if diff < self.mean_threshold:
                self.state = '2nd'
                self.score_2nd_step = 0
                logger.debug(f'Lvl up to the 2nd step')

            return self.get_current_state()

        # --------------------
        # Current state is 2nd
        # Update it with std value
        if self.state == '2nd':
            mean = np.std(data)
            diff = np.abs(mean - self.mean_ref_value)

            # --------------------
            # Check if the mean value fails to meet the threshold
            # if so, back to the 1st state
            if diff > self.mean_threshold:
                # Update rule:
                # It is basically the linear rule, but never
                # diff=  0 -> score=100
                # diff=100 -> score=0
                score = 100 - diff
                # Set the 1st step score as the correct value
                self.score_1st_step = score
                # Reset the 2nd step score to 0
                self.score_2nd_step = 0
                self._limit_scores()
                self.state = '1st'

                logger.debug(
                    f'Lvl down to the 1st step, 1st step score: {self.score_1st_step}')

            # --------------------
            # if the mean value is under the threshold,
            # update the score using std
            else:
                std = np.std(data)
                if std < self.std_threshold:
                    self.score_2nd_step += 10
                else:
                    self.score_2nd_step -= 10
                self._limit_scores()
                logger.debug(f'Updated 2nd step score: {self.score_2nd_step}')

            return self.get_current_state()

# --------------------------------------------------------------------------------


class AutomaticAnimation(object):
    width = 800
    height = 600

    font = ImageFont.truetype(
        root_path.joinpath('font/MSYHL.ttc').as_posix(),
        size=width//20)

    interval = 50  # ms, 50 ms refers 20 frames per second
    img = Image.new(mode='RGB', size=(width, height))
    fifo_buffer = []

    animating_flag = False

    @contextlib.contextmanager
    def _safe_animating_flag(self):
        try:
            self.animating_flag = True
            yield
        finally:
            self.animating_flag = False

    def animating_loop(self):
        """
        Perform animation by shifting the buffer.
        It keeps going in its own path, regardless others.

        ! The process updates the self.img in its own pace,
        ! so the UI only needs to fetch the self.img in UI's own pace.

        Args:
            self: The ScoreAnimation instance.

        Returns:
            None

        Examples:
            anim = ScoreAnimation()
            anim._animating()
        """

        secs = self.interval / 1000

        # Prevent repeated animation
        if self.animating_flag:
            logger.debug('Animating already on the loop')
            return

        with self._safe_animating_flag():
            while self._shift() is not None:
                time.sleep(secs)

        logger.debug('Finished animating')

    def _shift(self):
        """
        Shifts the score by popping an image from the stack and updating the current image.

        Args:
            self: The ScoreAnimation instance.

        Returns:
            img: The popped image from the stack, or None if the stack is empty.
        """

        img = self._pop()
        if img is not None:
            self.img = img
        return img

    def _pop(self):
        """
        Pops an image from the buffer.

        Args:
            self: The ScoreAnimation instance.

        Returns:
            img: The popped image from the buffer, or None if the buffer is empty.
        """

        if len(self.fifo_buffer) > 0:
            return self.fifo_buffer.pop(0)
        return

# --------------------------------------------------------------------------------


class TwoStepScore_Animation_CatLeavesSubmarine(TwoStepScorer, AutomaticAnimation):
    image_1st = None  # RGBA PIL image
    images_2nd = []  # RBG PIL images

    def __init__(self):
        self.load_cat_climbs_tree_resources()
        super(TwoStepScore_Animation_CatLeavesSubmarine, self).__init__()

    def load_cat_climbs_tree_resources(self):
        name = 'cat-leaves-submarine'
        folder = root_path.joinpath(f'img/{name}')

        for j in tqdm(range(1, 61), f'Loading resources: {name}'):
            img = Image.open(folder.joinpath(f'frames/{j}.jpg')).convert('RGB')
            img.resize((self.width, self.height))
            self.images_2nd.append(img)
        logger.debug(f'Loaded 60 frames of {name}')

        submarine_image = Image.open(
            folder.joinpath('parts/潜水艇.png')).convert('RGBA')
        self.submarine_image = submarine_image
        logger.debug(f'Loaded submarine image: {submarine_image}')

    def update_score(self, data: Any = None):
        state_before = self.get_current_state()

        # If received no data, the state is unchanged,
        # the state_after equals to state_before
        if data is None:
            state_after = state_before
        else:
            state_after = self._update_score(data)

        logger.debug(f'Updated state from {state_before} to {state_after}')
        self.mk_frames(state_before, state_after)

    def mk_frames(self, state_before, state_after):
        for img in self.images_2nd:
            self.fifo_buffer.append(img.resize((self.width, self.height)))

        Thread(target=self.animating_loop, daemon=True).start()
        pass


# %% ---- 2024-04-17 ------------------------
# Play ground


# %% ---- 2024-04-17 ------------------------
# Pending


# %% ---- 2024-04-17 ------------------------
# Pending
