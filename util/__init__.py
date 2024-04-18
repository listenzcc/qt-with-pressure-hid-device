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
from loguru import logger


# %% ---- 2023-09-17 ------------------------
# Function and class

#  Do not use Path(__file__) in the released version,
#  since it detects the runtime path of the exe, rather the cwd
root_path = Path(__file__).parent.parent

# Use this instead, it is more safety
root_path = Path(sys.argv[0]).parent

# %% ---- 2023-09-17 ------------------------
# Setup basic configure

# The configuration file is in 'conf/conf.yaml'
conf_path = root_path.joinpath('conf/conf.yaml')
conf_path.parent.mkdir(parents=True, exist_ok=True)

setup = dict(
    display=dict(
        window_length_seconds=20,  # Seconds
        delay_seconds=10,  # Seconds
        max_value=2000,  # g
        min_value=-10,  # g
        ref_value=500,  # g

        two_step_animation_mean_threshold=100,  # g
        two_step_animation_std_threshold=100,  # g
        two_step_animation_window_length=1.0,  # seconds

        display_ref_flag=True
    ),
    device=dict(
        sample_rate=125,  # Hz
        product_string='HIDtoUART example',  # name
        g0=int(open(root_path.joinpath('correction/g0')).read()),  # 44000
        g200=int(open(root_path.joinpath('correction/g200')).read()),  # 46000
        offset_g0=int(open(root_path.joinpath(
            'correction/offset_g0')).read()),  # same as g0
    ),
    experiment=dict(
        remainder=dict(
            Real='T',  # Feedback with the real pressure value
            Fake='F',  # Feedback with the fake (pseudo) pressure value
            Hide='H',  # Feedback is hided
            NA='--'  # Not available
        )
    )
)


project_conf = OmegaConf.create(setup)
print(OmegaConf.to_yaml(project_conf), file=open(conf_path, 'w'))


# %% ---- 2023-09-17 ------------------------
# logging

logger.add('log/pressure-feedback.log', rotation='1 MB')
logger.info(f'Project starts with: {project_conf}')


# %% ---- 2023-09-17 ------------------------
# Pending
