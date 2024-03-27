"""
File: compile_me.py
Author: Chuncheng Zhang
Date: 2023-09-21
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


# %% ---- 2023-09-21 ------------------------
# Requirements and constants
import subprocess
from pathlib import Path

root = Path(__file__).parent

# %% ---- 2023-09-21 ------------------------
# Function and class


def iter_ts_xml_files():
    yield from [e for e in root.iterdir() if e.name.endswith('.ts.xml')]


def compile_ts2qm(file):
    src = file.as_posix()
    dst = file.parent.joinpath(file.name.split('.')[0]).as_posix()

    subprocess.check_call(f'lrelease.exe "{src}" -qm "{dst}"')


# %% ---- 2023-09-21 ------------------------
# Play ground
if __name__ == '__main__':
    for f in iter_ts_xml_files():
        compile_ts2qm(f)


# %% ---- 2023-09-21 ------------------------
# Pending


# %% ---- 2023-09-21 ------------------------
# Pending
