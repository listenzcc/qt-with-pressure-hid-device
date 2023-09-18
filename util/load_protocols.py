"""
File: load_protocols.py
Author: Chuncheng Zhang
Date: 2023-09-18
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


# %% ---- 2023-09-18 ------------------------
# Requirements and constants
import json

from . import root, LOGGER


# %% ---- 2023-09-18 ------------------------
# Function and class

class MyProtocol(object):
    folder = root.joinpath('Protocols')

    def __init__(self):
        self.folder.mkdir(exist_ok=True, parents=True)
        self.default()
        LOGGER.debug(f'Initialized {self.__class__}')

    def default(self):
        self.protocols = dict()

        for path in self.folder.iterdir():
            if not all([
                path.is_file,
                path.name.endswith('.json'),
                path.name.startswith('Protocol')
            ]):
                continue

            k = path.name.replace('.json', '')

            self.protocols[k] = json.load(open(path))

            LOGGER.debug(f'Loaded protocol: {k}, {self.protocols[k]}')

    def get_buffer(self, key):
        return self.protocols[key]['_buffer']

    def save(self, name, buffer):
        for n in range(1000000):
            k = f'Protocol {n}'

            if k in self.protocols:
                continue

            self.protocols[k] = dict(
                name=name,
                maker='user',
                _buffer=buffer
            )

            p = self.folder.joinpath(f'{k}.json')

            json.dump(self.protocols[k], open(p, 'w'))

            LOGGER.debug(f'Saved protocol: {k} | {self.protocols[k]}')

            break


# %% ---- 2023-09-18 ------------------------
# Play ground


# %% ---- 2023-09-18 ------------------------
# Pending


# %% ---- 2023-09-18 ------------------------
# Pending
