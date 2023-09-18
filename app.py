"""
File: app.py
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
import time
import threading

from util import LOGGER, CONF
from util.real_time_hid_reader import TargetDevice, RealTimeHidReader
from util.qt_widget import QtWidgets, MyWidget, QtCore

# from util.qt_widget import QLineSeries, QPointF
# from rich import inspect
# inspect(QLineSeries(), all=True)
# inspect(QPointF(), all=True)

# %% ---- 2023-09-17 ------------------------
# Function and class


# %% ---- 2023-09-17 ------------------------
# Play ground

if __name__ == '__main__':

    target_device = TargetDevice()

    real_time_hid_reader = RealTimeHidReader(device=target_device.device)
    real_time_hid_reader.start()

    # time.sleep(10)
    # real_time_hid_reader.stop()
    # input('Press enter to escape.')

    app = QtWidgets.QApplication([])

    widget = MyWidget()
    # widget.resize(800, 600)
    widget.show()

    n = int(widget.window_length_seconds * real_time_hid_reader.sample_rate)
    nd = int(real_time_hid_reader.sample_rate *
             (widget.window_length_seconds - real_time_hid_reader.delay_seconds))

    def update():
        pairs = real_time_hid_reader.peek(n)
        pairs_delay = real_time_hid_reader.peek(nd, peek_delay=True)
        widget.update_graph(pairs, pairs_delay)

    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start()

    def exec():
        callback = app.exec()
        real_time_hid_reader.stop()
        time.sleep(1)
        return callback

    sys.exit(exec())


# %% ---- 2023-09-17 ------------------------
# Pending


# %% ---- 2023-09-17 ------------------------
# Pending
