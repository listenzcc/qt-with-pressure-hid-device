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
import json
import time
import threading
import contextlib
import opensimplex

import numpy as np

from . import logger, project_conf

# %% ---- 2023-09-17 ------------------------
# Function and class


def digit2int(bytes16: bytes) -> int:
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
    product_string = project_conf['device']['product_string']  # 'HIDtoUART example'

    def __init__(self):
        self.detect_product()
        logger.info(f'Initialized TargetDevice {self}')

    def detect_product(self):
        """Detect the product string of the target device

        Returns:
            device: The device I want;
            device_info (dict): The device info.
        """
        try:
            hid_devices = hid.enumerate()
            device_info = [
                e for e in hid_devices
                if e['product_string'] == self.product_string][0]
            device = hid.device()
            logger.debug(f'Detected device: {device_info}')
        except Exception as err:
            logger.error(f'Failed to detect the product, {err}')
            device_info = dict(
                error=f'Can not detect the product: {self.product_string}')
            device = None

        self.device_info = device_info
        self.device = device

        logger.debug(f'Detected device: {device}, {device_info}')

        return device, device_info

    @contextlib.contextmanager
    def open_path(self):
        path = 'No device'
        try:
            path = self.device_info.get('path', None)
            if self.device is None or path is None:
                yield None
            else:
                self.device.open_path(path)
                logger.debug(f'Opened path: {path}')
                yield self.device

        finally:
            if self.device is not None:
                self.device.close()
                logger.debug(f'Closed path: {path}')


class FakePressure(object):
    def __init__(self, data=None):
        self.load(data)
        logger.info(
            f'Initialized {self.__class__} with {self.n} time points, the first is {self.buffer[0]}')

    def load_file(self, file):
        data = json.load(open(file))
        return self.load(data)

    def load(self, data):
        if data is None:
            data = [
                (100, 45000, -1, -1, -1),
                (200, 46000, -1, -1, -1),
            ]
            logger.warning(
                'Load FakePressure with invalid data, using default instead.')

        n = len(data)
        d = np.array([e[0] for e in data])

        stats = dict(
            n=n,
            max=int(np.max(d)),
            min=int(np.min(d)),
            avg=int(np.average(d)),
            std=int(np.std(d))
        )

        self.buffer = data
        self.i = 0
        self.n = n

        logger.debug(f'Loaded FakePressure data: {stats}')

        return n, stats

    def get(self):
        '''
        Get the FakePressure data form the i-th position.

        Always follows,
        - the 1st value is pressure value,
        - the 2nd value is its digital.
        '''
        d = self.buffer[self.i]
        self.i += 1
        self.i %= self.n
        return d


class RealTimeHidReader(object):
    """
    The hid reader for real time getting the figure pressure value.

    ----------------------------------------------------------------------------------------------------
    - The buffer's columns (5) are
        (pressure_value, digital_value, fake_pressure_value, fake_digital_value, timestamp)

    - The buffer_delay's columns (5) are
        (avg-pressure, fake-avg-pressure, std-pressure, fake-std-pressure, timestamp)

    - The timestamp refers the seconds passed from the start
    ----------------------------------------------------------------------------------------------------

    @sample_rate (int): The frequency of getting the data;
    @running (boolean): The stats of the getting loop;
    @stop() (method): Stop the getting loop;
    @start() (method): Start the getting loop;
    @_reading() (private method):
        The getting loop function, it is a running-forever loop;
        The method updates the self.buffer in sample_rate frequency;
    @peek(n) (method): Peek the latest n-points data in the buffer;

    """

    sample_rate = int(project_conf['device']['sample_rate'])  # 125  # Hz
    delay_seconds = project_conf['display']['delay_seconds']
    delay_pnts = int(delay_seconds * sample_rate)

    g0 = project_conf['device']['g0']
    g200 = project_conf['device']['g200']
    offset_g0 = project_conf['device']['offset_g0']

    use_simplex_noise_flag = True  # False
    device_crush_flag = False

    pseudo_data = None
    fake_pressure = FakePressure()

    running = False

    def __init__(self, device: TargetDevice):
        self.device = device
        self.ts = 1 / self.sample_rate  # milliseconds

        logger.info(
            f'Initialized device: {self.device} with {self.sample_rate} | {self.ts}')

    def recompute_delay(self, delay_seconds: int):
        self.delay_seconds = delay_seconds
        self.delay_pnts = int(delay_seconds * self.sample_rate)
        logger.debug(
            f'Recompute delay: {self.delay_seconds} to {self.delay_pnts} points')

    def stop(self) -> list:
        """Stop the collecting loop.

        Returns:
            list: All the data collected.
        """
        self.running = False

        # if self.device is not None:
        #     # self.device.close()
        #     pass

        logger.debug('Stopped the HID device reading loop.')
        logger.debug(f'The session collected {len(self.buffer)} time points.')

        return self.buffer.copy()

    def start(self):
        """
        Start the getting loop in a thread.
        """

        t = threading.Thread(target=self._safe_reading, args=(), daemon=True)
        t.start()

        logger.debug('Started the HID device reading loop')

    def number2pressure(self, value: int) -> float:
        """
        Convert the value to the pressure value.

        output is:
            - 0, when value is self.offset_g0
            - 200, when value is different with the self.offset_g0 with 200 / (self.g200 - self.g0)

        Args:
            value (int): The input value.

        Returns:
            float: The converted pressure value. 
        """
        bias = self.offset_g0

        # ! Safe divide preventing g200 == g0
        k = 200 / max(100, self.g200 - self.g0)

        return (value - bias) * k
        # return (value - self.g0) / (self.g200 - self.g0) * 200.0

    def _safe_reading(self):
        '''
        It silently fails the self._reading() method if it crushes.
        The self.device_crush_flag is set accordingly.
        '''
        self.device_crush_flag = False
        try:
            self._reading()
        except Exception as err:
            self.device_crush_flag = True
            import traceback
            traceback.print_exc()
            logger.error(f'Device crushed: {err}')
        finally:
            logger.info(f'Stopped reading process')

    def _reading(self):
        """
        Private method of the getting loop.
        It is an infinity loop until self.stop() or self.running is False.
        """

        self.running = True

        self.buffer = []
        self.buffer_delay = []

        self.n = 0

        # device = self.device
        with self.device.open_path() as device:
            valid_device_flag = device is not None

            if not valid_device_flag:
                logger.warning('Invalid device')

            logger.debug('Starts the reading loop')

            tic = time.time()
            while self.running:
                t = time.time()

                if t < (tic + self.n * self.ts):
                    time.sleep(0.001)
                    continue

                if valid_device_flag:
                    # ! Case: The device is valid.
                    # Read real time pressure value and convert it
                    bytes16 = device.read(16)
                    raw_value = digit2int(bytes16)
                    value = self.number2pressure(raw_value)
                elif self.use_simplex_noise_flag:
                    # ! Case: The device is invalid, but we use the simplex noise.
                    # Debug usage when device is known to be invalid,
                    # use the opensimplex noise instead of real pressure
                    raw_value = (opensimplex.noise2(
                        x=10, y=t * 0.2)) * 2 * 1000 + 44064 + (46112 - 44064) * 2.5  # 200g
                    value = self.number2pressure(raw_value)
                else:
                    # ! Case: Otherwise, use -1, -1.
                    # Double -1 refers the device is invalid
                    raw_value = -1
                    value = -1

                # The 1st and 2nd elements are used as the fake pressure value
                fake = self.fake_pressure.get()

                # --------------------------------------------------------------------------------
                # Update buffer
                self.buffer.append((value, raw_value, fake[0], fake[1], t-tic))

                # The buffer grows by 1
                self.n += 1

                # Update buffer_delay
                if self.n > self.delay_pnts:
                    pairs = self.peek(self.delay_pnts)
                    values = [(e[0], e[2]) for e in pairs]
                    avg = tuple(np.mean(values, axis=0))
                    std = tuple(np.std(values, axis=0))
                    timestamp = t - tic - self.delay_seconds
                    # self.buffer_delay.append((avg, std, timestamp))
                    self.buffer_delay.append(avg+std+(timestamp,))

            t = time.time()
            logger.debug(
                f'Stopped the reading loop on {t}, lasting {t - tic} seconds.')

        return

    def peek_by_seconds(self, sec: float, peek_delay: bool = False) -> list:
        """
        Peeks at the next `n` samples from the HID device,
        where `n` is calculated based on the given number of seconds (`sec`) and the sample rate of the device.

        Args:
            sec (float): The number of seconds to peek at.

        Returns:
            list: A list of the next `n` samples from the HID device.
        """

        n = int(sec * self.sample_rate)
        return self.peek(n, peek_delay)

    def peek(self, n: int, peek_delay: bool = False) -> list:
        """Peek the latest n-points data

        Args:
            n (int): The count of points to be peeked;

        Returns:
            list:
                The got data, [(value, t), ...], value is the data value, t is the timestamp.
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
