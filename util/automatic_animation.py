"""
File: automatic_animation.py
Author: Chuncheng Zhang
Date: 2024-04-19
Copyright & Email: chuncheng.zhang@ia.ac.cn

Purpose:
    Automatic animation

Functions:
    1. Requirements and constants
    2. Function and class
    3. Play ground
    4. Pending
    5. Pending
"""


# %% ---- 2024-04-19 ------------------------
# Requirements and constants
import time
import contextlib
import numpy as np

from PIL import ImageFont, Image, ImageDraw

from . import root_path, logger


# %% ---- 2024-04-19 ------------------------
# Function and class

class AutomaticAnimation(object):
    width = 800
    height = 600

    font = ImageFont.truetype(
        root_path.joinpath('font/MSYHL.ttc').as_posix(),
        size=width//20)

    interval = 50  # ms, 50 ms refers 20 frames per second
    img = Image.new(mode='RGB', size=(width, height))
    fifo_buffer = []

    animating_flag = False

    @contextlib.contextmanager
    def _safe_animating_flag(self):
        try:
            self.animating_flag = True
            yield
        finally:
            self.animating_flag = False

    def animating_loop(self):
        """
        Perform animation by shifting the buffer.
        It keeps going in its own path, regardless others.

        ! The process updates the self.img in its own pace,
        ! so the UI only needs to fetch the self.img in UI's own pace.

        Args:
            self: The ScoreAnimation instance.

        Returns:
            None

        Examples:
            anim = ScoreAnimation()
            anim._animating()
        """

        secs = self.interval / 1000

        # Prevent repeated animation
        if self.animating_flag:
            logger.debug('Animating already on the loop')
            return

        with self._safe_animating_flag():
            while self._shift() is not None:
                time.sleep(secs)

        logger.debug('Finished animating')

    def _shift(self):
        """
        Shifts the score by popping an image from the stack and updating the current image.

        Args:
            self: The ScoreAnimation instance.

        Returns:
            img: The popped image from the stack, or None if the stack is empty.
        """

        img = self._pop()
        if img is not None:
            self.img = img
        return img

    def _pop(self):
        """
        Pops an image from the buffer.

        Args:
            self: The ScoreAnimation instance.

        Returns:
            img: The popped image from the buffer, or None if the buffer is empty.
        """

        if len(self.fifo_buffer) > 0:
            return self.fifo_buffer.pop(0)
        return

    def _scale_x_ratio(self, x: float) -> int:
        return int(x * self.width)

    def _scale_y_ratio(self, y: float) -> int:
        return int(y * self.height)

    def scale_xy_ratio(self, xy: tuple) -> tuple:
        x, y = xy
        return (self._scale_x_ratio(x), self._scale_y_ratio(y))

    def _scale_value_to_tiny_window(self, xy_array: np.ndarray, ref: float = 0.0, copy: bool = False) -> np.ndarray:
        # The pos of the tiny window
        # By design, the data is plotted in the y-axis linearly.
        # The ref equals to the half_height
        # The ratio values refer the ratios of the image
        x_offset = 0.7
        y_offset = 0.5
        window_width = 0.2
        height_of_200g = 0.2

        xy_array = np.array(xy_array).astype(np.float32, copy=copy)

        x_array = xy_array[:, 0]
        x_array *= window_width
        x_array += x_offset
        x_array *= self.width

        y_array = xy_array[:, 1]
        y_array -= ref
        y_array /= -200
        y_array *= height_of_200g
        y_array += y_offset
        y_array *= self.height

        return xy_array

    def tiny_window(self, ref=0, data=None):
        """
        Creates a tiny-window widget by drawing reference and real-time curves on the given image.

        Args:
            self: The ScoreAnimation instance.
            img: The image to draw the curves on.
            ref (int, optional): The reference value. Defaults to 0.
            pairs (list, optional): List of value pairs. Each pair represents a point on the real-time curve. Defaults to None.

        Returns:
            img: The image with the reference and real-time curves drawn.

        Examples:
            anim = ScoreAnimation()
            img = Image.new('RGB', (800, 600))
            img = anim.tiny_window(img, ref=10, pairs=[(5,), (8,), (12,)])
        """

        # Parse the input pairs
        # If pairs is None, only draw the ref
        if data is None:
            data = [(ref, 0, 0), (ref, 0, 0)]

        # If pairs contain no data, only draw the ref
        if len(data) == 0:
            data = [(ref, 0, 0), (ref, 0, 0)]

        # If pairs contain only one point, make it two
        if len(data) == 1:
            data.append(data[0])

        data = np.array(data)

        n = len(data)
        x = np.linspace(0, 1, n)
        avg_y = data[:, 0]
        std_latest = data[-1, 1]

        # Where the tiny window is drawn
        img = self.img.copy()
        draw = ImageDraw.Draw(img, mode='RGB')

        # Draw the reference line
        draw.line(self._scale_value_to_tiny_window(
            np.array([[0, ref], [1, ref]]), ref=ref), fill='green')

        # Draw the avg. curve
        xy = np.concatenate([x[:, np.newaxis], avg_y[:, np.newaxis]], axis=1)
        draw.line(self._scale_value_to_tiny_window(xy, ref=ref), fill='red')

        # Draw the std. range
        draw.line(self._scale_value_to_tiny_window(
            np.array([[1, ref-std_latest], [1, ref+std_latest]]), ref=ref), fill='gray')

        return img


# %% ---- 2024-04-19 ------------------------
# Play ground


# %% ---- 2024-04-19 ------------------------
# Pending


# %% ---- 2024-04-19 ------------------------
# Pending
