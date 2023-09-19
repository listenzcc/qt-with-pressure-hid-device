"""
File: real_time_hid_reader.py
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
import hid
import time
import random
import threading
import opensimplex

import numpy as np

from . import LOGGER, CONF

# %% ---- 2023-09-17 ------------------------
# Function and class


def digit2int(bytes16):
    """Convert 16 bytes buffer into integer

    Args:
        bytes16 (bytes): The input 16 bytes buffer.

    Returns:
        int: The converted integer.
    """
    b4 = bytes16[4]
    b3 = bytes16[3]
    decoded = b4 * 256 + b3
    return decoded


class TargetDevice(object):
    """The hid device of interest,
    it is a figure pressure A/D machine.

    @product_string (string): The product string of the target device.

    @detect_product() (method): Automatically detect the device.

    """
    product_string = CONF['device']['product_string']  # 'HIDtoUART example'

    def __init__(self):
        self.detect_product()
        pass

    def detect_product(self):
        try:
            hid_devices = hid.enumerate()
            device_info = [e for e in hid_devices
                           if e['product_string'] == self.product_string][0]
            device = hid.Device(path=device_info['path'])
        except Exception as err:
            LOGGER.error(f'Failed to detect the product, {err}')
            device_info = dict(
                error=f'Can not detect the product: {self.product_string}')
            device = None
            pass

        self.device_info = device_info
        self.device = device

        return device, device_info


class RealTimeHidReader(object):
    """The hid reader for real time getting the figure pressure value.

    @sample_rate (int): The frequency of getting the data;
    @running (boolean): The stats of the getting loop;
    @stop() (method): Stop the getting loop;
    @start() (method): Start the getting loop;
    @_reading() (private method): The getting loop function, it is a running-forever loop;
                                  The method updates the self.buffer in sample_rate frequency;
    @peek(n) (method): Peek the latest n-points data in the buffer;

    """

    sample_rate = int(CONF['device']['sample_rate'])  # 125  # Hz
    window_length_seconds = CONF['display']['window_length_seconds']
    delay_seconds = CONF['display']['delay_seconds']

    g0 = CONF['device']['g0']
    g200 = CONF['device']['g200']

    running = False

    def __init__(self, device):
        self.device = device
        self.ts = 1 / self.sample_rate  # milliseconds

        LOGGER.debug(
            f'Initialized device: {self.device} with {self.sample_rate} | {self.ts}')

    def stop(self):
        """Stop the getting loop.
        """
        self.running = False

        if self.device is not None:
            self.device.close()

        LOGGER.debug('Stopped the HID device reading loop.')
        LOGGER.debug(f'The session collects {len(self.buffer)} time points.')

        return self.buffer.copy()

    def start(self):
        """Start the getting loop.
        """
        t = threading.Thread(target=self._reading, args=(), daemon=True)
        t.start()

        LOGGER.debug('Started the HID device reading loop')

    def number2pressure(self, value):
        return (value - self.g0) / (self.g200 - self.g0) * 200.0

    def _reading(self):
        """Private method of the getting loop.
        """
        self.running = True

        self.buffer = []
        self.buffer_delay = []

        self.n = 0
        self.nd = 0

        device = self.device
        valid_device_flag = device is not None
        delay_pnts = int(self.delay_seconds * self.sample_rate)

        LOGGER.debug('Starts the reading loop')

        t0 = time.time()
        while self.running:
            t = time.time()

            if t < (t0 + self.n * self.ts):
                time.sleep(0.001)
            else:
                if valid_device_flag:
                    bytes16 = device.read(16, timeout=100)
                    value = digit2int(bytes16)
                else:
                    value = (opensimplex.noise2(
                        x=10, y=t * 0.2) + 1) * 10000 + 44000
                    # x = random.randint(40000, 60000)

                value = self.number2pressure(value)

                self.buffer.append((value, t-t0))
                self.n += 1

                if self.n > delay_pnts:
                    pairs = self.peek(delay_pnts)
                    values = [e[0] for e in pairs]
                    mean = np.mean(values)
                    std = np.mean(values)
                    max = np.max(values)
                    min = np.min(values)
                    timestamp = t - t0 - self.delay_seconds
                    self.buffer_delay.append((mean, std, max, min, timestamp))
                    self.nd += 1

                # if self.n % self.sample_rate == 0:
                #     print(self.n // self.sample_rate, len(self.buffer))

        t = time.time()
        LOGGER.debug(
            f'Stopped the reading loop on {t}, lasting {t - t0} seconds.')

        return

    def peek(self, n, peek_delay=False):
        """Peek the latest n-points data

        Args:
            n (int): The count of points to be peeked;
            peek_delay (boolean): Whether peek the buffer_delay.

        Returns:
            array: The got data, [(value, t), ...], value is the data value, t is the timestamp.
                   If peek_delay, the buffer_delay is used, [(mean, std, max, min, timestamp), ...] is is the format.
        """
        if peek_delay:
            return self.buffer_delay[-n:]

        return self.buffer[-n:]


# %% ---- 2023-09-17 ------------------------
# Play ground


# %% ---- 2023-09-17 ------------------------
# Pending


# %% ---- 2023-09-17 ------------------------
# Pending
