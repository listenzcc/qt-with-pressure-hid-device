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
import sys
from pathlib import Path
from datetime import datetime
from omegaconf import OmegaConf
from loguru import logger as LOGGER


# %% ---- 2023-09-17 ------------------------
# Function and class

root_path = Path(__file__).parent.parent
root_path = Path(sys.argv[0]).parent

# %% ---- 2023-09-17 ------------------------
# conf
conf_path = root_path.joinpath('conf/conf.yaml')
conf_path.parent.mkdir(parents=True, exist_ok=True)

setup = dict(
    display=dict(
        window_length_seconds=20,  # Seconds
        delay_seconds=10,  # Seconds
        max_value=2000,
        min_value=-10,
        ref_value=500,
        display_ref_flag=True
    ),
    device=dict(
        sample_rate=125,  # Hz
        product_string='HIDtoUART example',  # name
        g0=int(open(root_path.joinpath('correction/g0')).read()),  # 44000,
        g200=int(open(root_path.joinpath('correction/g200')).read())  # 46000,
    ),
    experiment=dict(
        remainder=dict(
            Real='T',
            Fake='F',
            NA='--'
        )
    )
)


CONF = OmegaConf.create(setup)
print(OmegaConf.to_yaml(CONF), file=open(conf_path, 'w'))


# %% ---- 2023-09-17 ------------------------
# logging
logger_path = root_path.joinpath(
    f'log/{datetime.strftime(datetime.now(), "%Y-%m-%d")}.log')
logger_path.parent.mkdir(parents=True, exist_ok=True)

LOGGER.add(logger_path)
LOGGER.info(f'Project starts with: {CONF}')


# %% ---- 2023-09-17 ------------------------
# Pending
