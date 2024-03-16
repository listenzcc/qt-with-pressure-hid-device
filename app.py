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

from util import LOGGER, CONF, root_path
from util.real_time_hid_reader import TargetDevice, RealTimeHidReader
from util.qt_widget import QtWidgets, UserInterfaceWidget, QtCore, app

# from util.qt_widget import QLineSeries, QPointF
# from rich import inspect
# inspect(QLineSeries(), all=True)
# inspect(QPointF(), all=True)

# %% ---- 2023-09-17 ------------------------
# Function and class


# %% ---- 2023-09-17 ------------------------
# Play ground

if __name__ == "__main__":
    target_device = TargetDevice()

    real_time_hid_reader = RealTimeHidReader(device=target_device)

    # app = QtWidgets.QApplication([])

    translator = QtCore.QTranslator(app)

    lang = "zh_CN"
    # lang = 'en_US'
    path = root_path.joinpath(f"translate/{lang}")
    if translator.load(path.as_posix()):
        app.installTranslator(translator)
        LOGGER.debug(f"Translator is loaded: {lang}: {path}")
    else:
        LOGGER.error(f"Failed to load translator: {lang}: {path}")

    widget = UserInterfaceWidget(app)
    widget.restart_reader(real_time_hid_reader)
    widget.show()

    def exec():
        callback = app.exec_()
        real_time_hid_reader.stop()
        time.sleep(1)
        return callback

    sys.exit(exec())


# %% ---- 2023-09-17 ------------------------
# Pending


# %% ---- 2023-09-17 ------------------------
# Pending
