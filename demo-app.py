"""
File: demo-app.py
Author: Chuncheng Zhang
Date: 2023-09-14
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


# %% ---- 2023-09-14 ------------------------
# Requirements and constants
import hid
import time
import threading

import pandas as pd

from rich import print, inspect

import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QPainter
from PySide6.QtCore import QDateTime, Qt
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis


# %% ---- 2023-09-14 ------------------------
# Function and class


def digit2int(buffer):
    b4 = buffer[4]
    b3 = buffer[3]
    decoded = b4 * 256 + b3
    return decoded


class RealTimeHidReader(object):
    sample_rate = 125  # Hz
    running = False

    def __init__(self, device):
        self.device = device
        self.ts = 1 / self.sample_rate  # milliseconds

    def stop(self):
        self.running = False

        if self.device is not None:
            self.device.close()

    def start(self):
        self.buffer = []
        self.n = 0
        self.m = 0
        t = threading.Thread(target=self.reading, args=(), daemon=True)
        t.start()

    def reading(self):
        self.running = True

        device = self.device

        t0 = time.time()
        while self.running:
            t = time.time()

            if t >= (t0 + self.n * self.ts):
                if device is not None:
                    buffer16 = device.read(16, timeout=100)

                    if len(buffer16) != 16:
                        print(buffer16, len(buffer16))

                    x = digit2int(buffer16)
                    print(x)
                else:
                    x = random.randint(40000, 60000)

                self.buffer.append((x, t))
                self.n += 1

                if self.n % self.sample_rate == 0:
                    print(self.n // self.sample_rate, len(self.buffer))

    def peek(self, n):
        return self.buffer[-n:]

    def get(self):
        if self.m < self.n:
            self.m += 1
            return self.buffer[self.m-1][0]
        return None


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        # Creating QChart
        self.chart = QChart()
        # self.chart.setAnimationOptions(QChart.AllAnimations)
        self.add_series("Magnitude (Column 1)", [0, 1])

        # Creating QChartView
        self.chart_view = QChartView(self.chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.chart_view)

        self.button.clicked.connect(self.magic)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))
        self.update()

    def update(self, y=None):
        if y is None:
            y = -random.randint(40000, 60000)

        self.series.append(self.series.x, y)
        self.series.x += 1
        self.series.remove(0)
        self.axis_x.setMax(self.series.x)
        self.axis_x.setMin(self.series.x - 500)

    def add_series(self, name, columns):
        # Create QLineSeries
        self.series = QLineSeries()
        self.series.setName(name)

        for x in range(500):
            self.series.append(x, random.randint(40000, 60000))

        self.series.x = 500

        # # Filling QLineSeries
        # for i in range(self.model.rowCount()):
        #     # Getting the data
        #     t = self.model.index(i, 0).data()
        #     date_fmt = "yyyy-MM-dd HH:mm:ss.zzz"

        #     x = QDateTime().fromString(t, date_fmt).toSecsSinceEpoch()
        #     y = float(self.model.index(i, 1).data())

        #     if x > 0 and y > 0:
        #         self.series.append(x, y)

        self.chart.addSeries(self.series)

        # # Setting X-axis
        self.axis_x = QValueAxis()
        # self.axis_x.setTickCount(10)
        # self.axis_x.setFormat("dd.MM (h:mm)")
        # self.axis_x.setTitleText("Date")
        self.chart.addAxis(self.axis_x, Qt.AlignBottom)
        self.series.attachAxis(self.axis_x)
        # # Setting Y-axis
        self.axis_y = QValueAxis()
        # self.axis_y.setTickCount(10)
        self.axis_y.setLabelFormat("%.2f")
        self.axis_y.setTitleText("Magnitude")
        self.chart.addAxis(self.axis_y, Qt.AlignLeft)
        self.series.attachAxis(self.axis_y)

        # # Getting the color from the QChart to use it on the QTableView
        # color_name = self.series.pen().color().name()
# %% ---- 2023-09-14 ------------------------
# Play ground


device = None

try:
    hid_devices = hid.enumerate()
    selected = [e for e in hid_devices
                if e['product_string'] == 'HIDtoUART example'][0]
    device = hid.Device(path=selected['path'])
    print(selected, device)
except IndexError:
    print('Can not find my hid device')
    pass

rthr = RealTimeHidReader(device)
rthr.start()

# time.sleep(10)

# %% ---- 2023-09-14 ------------------------
# Pending
if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MyWidget()
    widget.resize(800, 600)
    widget.show()

    def foo():
        while True:
            y = rthr.get()
            if y is not None:
                widget.update(y)

    t = threading.Thread(target=foo, daemon=True)
    t.start()

    sys.exit(app.exec())

# %% ---- 2023-09-14 ------------------------
# Pending
