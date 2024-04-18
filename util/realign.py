"""
File: realign.py
Author: Chuncheng Zhang
Date: 2024-03-24
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Realign the sampled data into 8ms sampling

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-03-24 ------------------------
# Requirements and constants
import numpy as np
import scipy.interpolate

from . import logger


# %% ---- 2024-03-24 ------------------------
# Function and class
def realign_into_8ms_sampling(data: list) -> np.ndarray:
    """
    Re-aligns the given data to 8 milliseconds sampling.

    Args:
        data (list): The input data to be re-aligned.

    Returns:
        np.ndarray: The re-aligned data with columns (pressure_value, digital_value, fake_pressure_value, fake_digital_value, seconds passed from the start).
    """
    # Make sure the sampling time is strictly increasing sequence
    # 1. Unique values
    m = len(data)
    d = [data[0]]
    for i in range(1, m):
        if data[i][-1] != d[-1][-1]:
            d.append(data[i])
    data = d
    m = len(data)

    # 2. Make it increasing
    data = np.array(sorted(data, key=lambda e: e[-1]))

    # ! Columns of data is
    # ! (pressure_value, digital_value, fake_pressure_value, fake_digital_value,seconds passed from the start)
    # Re-align the data to 8 milliseconds sampling
    # It equals to 125 Hz.
    max_t = data[-1, -1]
    x_realign = np.arange(0, max_t, 0.008)

    # 1. Get the sampling times
    x_sampling = data[:, 4]  # Sampling times # np.array([e[4] for e in data])

    # 2. Prepare the output data frame
    n = len(x_realign)
    realigned = np.zeros((n, 5))
    realigned[:, 4] = x_realign

    # 3. Setup the interoplate class as worker
    worker = scipy.interpolate.CubicSpline

    # 4. Interploate the other columns
    for i in range(4):
        interpolator = worker(x=x_sampling, y=data[:, i])
        realigned[:, i] = interpolator(x_realign)

    logger.debug(
        f'Realigned the data with {m} -> {n} points, interpolator is {worker}')

    return realigned.tolist()


# %% ---- 2024-03-24 ------------------------
# Play ground


# %% ---- 2024-03-24 ------------------------
# Pending


# %% ---- 2024-03-24 ------------------------
# Pending
