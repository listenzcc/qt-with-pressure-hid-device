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

from . import root_path, LOGGER


# %% ---- 2023-09-18 ------------------------
# Function and class

class MyProtocol(object):
    folder = root_path.joinpath('Protocols')

    def __init__(self):
        self.folder.mkdir(exist_ok=True, parents=True)
        self.default()
        LOGGER.debug(f'Initialized {self.__class__}')

    def default(self):
        """
        Executes the default behavior of the object.

        This method initializes the `protocols` attribute as an empty dictionary.
        It then iterates over the files in the `folder` attribute and loads any JSON files that start with 'Protocol' and end with '.json'. The loaded protocols are stored in the `protocols` dictionary with the file name (without the extension) as the key.

        Args:
            self: The object instance.

        Returns:
            None

        Example:
            ```python
            obj = ClassName()
            obj.default()
            ```
        """

        self.protocols = {}

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
        """
        Returns the buffer associated with the given key from the `protocols` dictionary.

        This method retrieves the value of the `_buffer` key from the dictionary stored in the `protocols` attribute, using the provided `key` as the dictionary key.

        Args:
            self: The object instance.
            key: The key used to retrieve the buffer from the `protocols` dictionary.

        Returns:
            The buffer associated with the given key.

        Example:
            ```python
            obj = ClassName()
            buffer = obj.get_buffer('key')
            ```
        """

        return self.protocols[key]['_buffer']

    def save(self, name: str, buffer: dict):
        """
        Saves a protocol with the given name and buffer.

        This method creates a new protocol entry in the `protocols` dictionary.
        It generates a unique key for the protocol by incrementing a number starting from 0 and prepending it with 'Protocol'.
        If a protocol with the generated key already exists, the method continues to generate a new key until a unique one is found.
        The protocol entry includes the provided `name`, a maker value of 'user', and the provided `buffer`.
        The protocol is then saved as a JSON file in the `folder` directory.

        Args:
            self: The object instance.
            name (str): The name of the protocol.
            buffer (dict): The buffer associated with the protocol.

        Returns:
            None

        Example:
            ```python
            obj = ClassName()
            obj.save('protocol_name', {'key': 'value'})
            ```
        """

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
