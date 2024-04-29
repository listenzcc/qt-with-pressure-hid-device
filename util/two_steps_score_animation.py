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
import numpy as np

from PIL import Image, ImageDraw
from threading import Thread

from typing import Any
from tqdm.auto import tqdm

from . import logger, project_conf, root_path
from .automatic_animation import AutomaticAnimation


# %% ---- 2024-04-17 ------------------------
# Function and class

# --------------------------------------------------------------------------------
class TwoStepScorer(object):
    ref_value = project_conf['display']['ref_value']
    mean_threshold = 50  # g
    std_threshold = 50  # g

    state = '1st'

    # DO NOT control the score_1st, since it is the mean value
    score_1st = 0

    # Control the score_2nd, it refers the standard value
    score_2nd = 0
    score_2nd_range = (0, 100)

    def __init__(self):
        self.reset_scores()
        logger.info("Initialized TwoStepScorer")

    def reset_scores(self):
        self.state = '1st'
        self.score_1st = 0
        self.score_2nd = 0
        logger.debug('Reset the TwoStepScorer')

    def get_current_state(self):
        return dict(
            state=self.state,
            score_1st=self.score_1st,
            score_2nd=self.score_2nd,
        )

    def _limit_scores(self):
        '''Keep the scores inside the range of [0, 100]'''
        # self.score_1st = min(100, max(0, self.score_1st))
        self.score_2nd = min(self.score_2nd_range[1], max(
            self.score_2nd_range[0], self.score_2nd))

    def _update_score(self, data: Any):
        if data is None:
            return self.get_current_state()

        if len(data) == 0:
            return self.get_current_state()

        mean = data[-1][0]
        std = data[-1][1]

        logger.debug(f'Update score, input is mean={mean}, std={std}')

        # --------------------
        # Current state is 1st
        # Update it with mean value
        if self.state == '1st':
            # Update the score
            score = mean - self.ref_value
            self.score_1st = score
            self._limit_scores()

            # The mean value meets the threshold, enter into the 2nd step
            diff = np.abs(score)
            if diff < self.mean_threshold:
                self.state = '2nd'
                self.score_2nd = 0
                logger.debug(f'Lvl up to the 2nd step')

            return self.get_current_state()

        # --------------------
        # Current state is 2nd
        # Update it with std value
        if self.state == '2nd':
            diff = np.abs(mean - self.ref_value)

            # --------------------
            # Check if the mean value fails to meet the threshold
            # if so, back to the 1st state
            if diff > self.mean_threshold:
                # Update rule:
                score = mean - self.ref_value
                self.score_1st = score
                # Reset the 2nd step score to 0
                self.score_2nd = 0
                self._limit_scores()
                self.state = '1st'

                logger.debug(
                    f'Lvl down to the 1st step, 1st step score: {self.score_1st}')

            # --------------------
            # if the mean value is under the threshold,
            # update the score using std
            else:
                if std < self.std_threshold:
                    self.score_2nd += 10
                else:
                    self.score_2nd -= 10
                self._limit_scores()
                logger.debug(f'Updated 2nd step score: {self.score_2nd}')

            return self.get_current_state()


# --------------------------------------------------------------------------------


class TwoStepScore_Animation_CatLeavesSubmarine(TwoStepScorer, AutomaticAnimation):
    images_2nd = []  # RBG PIL images

    def __init__(self):
        self.load_cat_climbs_tree_resources()
        super(TwoStepScore_Animation_CatLeavesSubmarine, self).__init__()

    def reset(self):
        self.fifo_buffer = []
        self.reset_scores()

    def load_cat_climbs_tree_resources(self):
        name = 'cat-leaves-submarine'
        folder = root_path.joinpath(f'img/{name}')

        # --------------------
        # ! The relative small size of the image
        # ! The aim is to minimize the working load of the imaging
        image_size = (self.width, self.height)

        # --------------------
        # Load frames
        n = 60
        # n = 6
        self.images_2nd = []
        for j in tqdm(range(n), f'Loading frames: {name}'):
            img = Image.open(folder.joinpath(f'frames/{j+1}.jpg'))
            self.images_2nd.append(img)
        logger.debug(f'Loaded {n} frames of {name}')

        # --------------------
        # Load the ocean image
        ocean_image = Image.open(folder.joinpath('parts/ocean-only.jpg'))
        logger.debug('Loaded ocean image')

        # --------------------
        # Load submarine image and generate its mask
        submarine_image = Image.open(
            folder.joinpath('parts/submarine-only.jpg'))
        logger.debug('Loaded submarine image')

        mat = np.array(submarine_image.convert('L'))
        _mat = mat.copy()
        mat[_mat < 250] = 255
        mat[_mat >= 250] = 0

        submarine_mask = Image.fromarray(mat, mode='L')
        logger.debug('Generated submarine image')

        # --------------------
        self.images_2nd
        self.image_size = image_size
        self.ocean_image = ocean_image
        self.submarine_image = submarine_image
        self.submarine_mask = submarine_mask

    def update_score(self, data: Any = None):
        state_before = self.get_current_state()

        # If received no data, the state is unchanged,
        # the state_after equals to state_before
        state_after = state_before if data is None else self._update_score(
            data)

        logger.debug(f'Updated state from {state_before} to {state_after}')
        self.mk_frames(state_before, state_after)

    def mk_frames(self, state_before, state_after):

        n_frames = 10

        image_size = (self.width, self.height)

        # --------------------
        # The 2nd state
        # Only choose the frames to display
        if state_after['state'] == '2nd':
            score1 = state_before['score_2nd']
            score2 = state_after['score_2nd']
            diff = score2 - score1

            n = len(self.images_2nd)-1

            # Handle the both conditions of diff == 0 and diff != 0
            for score in [score1] if diff == 0 else np.arange(score1, score2+diff/n_frames/2, diff/n_frames):
                idx = int((n-1) * score / self.score_2nd_range[1])
                img = self.images_2nd[idx].resize(image_size)

                # # --------------------
                # draw = ImageDraw.Draw(img, mode='RGB')
                # r = 0.04
                # x = 0.5
                # y = 0.8
                # draw.rectangle((
                #     self.scale((x-r, y-r)), self.scale((x+r, y+r))
                # ), fill='#00aaaa')

                self.fifo_buffer.append(img)

        # --------------------
        # The 1st state
        # Put the submarine on the correct position
        if state_after['state'] == '1st':
            score1 = state_before['score_1st']
            score2 = state_after['score_1st']

            # At least make the score2 of the same sign with the score1,
            # it prevents the submarine up and down
            if score1 * score2 < 0:
                score2 *= -1

            diff = score2 - score1

            score_scale = 100  # g
            _, height = self.submarine_image.size
            max_d_height = height * 0.2

            # Handle the both conditions of diff == 0 and diff != 0
            for score in [score1] if diff == 0 else np.arange(score1, score2+diff/n_frames/2, diff/n_frames):
                img = self.ocean_image.copy()
                # score -> infinity, dy -> 1
                # score -> 0, dy -> 0
                dy = (1 - np.exp(-np.abs(score / score_scale)))
                img.paste(
                    self.submarine_image,
                    (0, int(dy * max_d_height)),
                    self.submarine_mask)
                img = img.resize(image_size)

                # # --------------------
                # draw = ImageDraw.Draw(img, mode='RGB')
                # r = 0.05
                # x = 0.5
                # y = 0.8
                # draw.rectangle((
                #     self.scale((x-r, y-r)), self.scale((x+r, y+r))
                # ), outline='#aaaaaa')

                # # --------------------
                # r = 0.04
                # x = 0.5 + 0.5 * score2 / 200
                # y = 0.8
                # draw.rectangle((
                #     self.scale((x-r, y-r)), self.scale((x+r, y+r))
                # ), outline='#aa0000')

                # # --------------------
                # r = 0.04
                # x = 0.5 + 0.5 * score / 200
                # y = 0.8
                # draw.rectangle((
                #     self.scale((x-r, y-r)), self.scale((x+r, y+r))
                # ), fill='#aa0000')

                self.fifo_buffer.append(img)

        Thread(target=self.animating_loop, daemon=True).start()

    def scale(self, xy: tuple) -> tuple:
        return self.scale_xy_ratio(xy)


# %% ---- 2024-04-17 ------------------------
# Play ground


# %% ---- 2024-04-17 ------------------------
# Pending


# %% ---- 2024-04-17 ------------------------
# Pending
