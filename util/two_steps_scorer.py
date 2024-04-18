"""
File: two_steps_scorer.py
Author: Chuncheng Zhang
Date: 2024-04-17
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    It is a two-steps scorer.
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
from . import LOGGER, CONF


# %% ---- 2024-04-17 ------------------------
# Function and class
class TwoStepScorer(object):
    mean_ref_value = CONF['display']['ref_value']
    mean_threshold = CONF['display']['two_step_animation_mean_threshold']
    std_threshold = CONF['display']['two_step_animation_std_threshold']
    window_length = CONF['display']['two_step_animation_window_length']

    state = '1st'
    score_1st_step = 0
    score_2nd_step = 0

    def __init__(self):
        self.reset()
        LOGGER.info("Initialized TwoStepScorer")

    def reset(self):
        self.state = '1st'
        self.score_1st_step = 0
        self.score_2nd_step = 0
        LOGGER.debug('Reset the TwoStepScorer')

    def limit_scores(self):
        '''Keep the scores inside the range of [0, 100]'''
        self.score_1st_step = min(100, max(0, self.score_1st_step))
        self.score_2nd_step = min(100, max(0, self.score_2nd_step))

    def update(self, data: list):
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
            self.limit_scores()

            # The mean value meets the threshold, enter into the 2nd step
            if diff < self.mean_threshold:
                self.state = '2nd'
                self.score_2nd_step = 0
                LOGGER.debug(f'Lvl up to the 2nd step')

            return

        # Current state is 2nd
        # Update it with std value
        if self.state == '2nd':
            mean = np.std(data)
            diff = np.abs(mean - self.mean_ref_value)

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
                self.limit_scores()
                self.state = '1st'
                LOGGER.debug(
                    f'Lvl down to the 1st step, 1st step score: {self.score_1st_step}')
                return

            std = np.std(data)
            if std < self.std_threshold:
                self.score_2nd_step += 10
            else:
                self.score_2nd_step -= 10
            self.limit_scores()
            LOGGER.debug(f'Updated 2nd step score: {self.score_2nd_step}')


# %% ---- 2024-04-17 ------------------------
# Play ground


# %% ---- 2024-04-17 ------------------------
# Pending


# %% ---- 2024-04-17 ------------------------
# Pending
