"""
File: __init__.py
Author: Chuncheng Zhang
Date: 2023-09-17
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


# %% ---- 2023-09-17 ------------------------
# Requirements and constants
from pathlib import Path
from datetime import datetime
from omegaconf import OmegaConf
from loguru import logger as LOGGER


# %% ---- 2023-09-17 ------------------------
# Function and class

root = Path(__file__).parent.parent

# %% ---- 2023-09-17 ------------------------
# conf
conf_path = root.joinpath('conf/conf.yaml')
conf_path.parent.mkdir(parents=True, exist_ok=True)

setup = dict(
    display=dict(
        window_length_seconds=20,  # Seconds
        delay_seconds=10  # Seconds
    ),
    device=dict(
        sample_rate=125,  # Hz
        product_string='HIDtoUART example',  # name
        g0=44000,
        g200=46000
    )
)


CONF = OmegaConf.create(setup)
print(OmegaConf.to_yaml(CONF), file=open(conf_path, 'w'))


# %% ---- 2023-09-17 ------------------------
# logging
logger_path = root.joinpath(
    f'log/{datetime.strftime(datetime.now(), "%Y-%m-%d")}.log')
logger_path.parent.mkdir(parents=True, exist_ok=True)

LOGGER.add(logger_path)
LOGGER.info(f'Project starts with: {CONF}')


# %% ---- 2023-09-17 ------------------------
# Pending
