"""
File: qt_widget.py
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
# import matplotlib
# matplotlib.use('Qt5Agg')  # noqa

import random

import pyqtgraph as pg

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QIntValidator

from . import LOGGER, CONF

# %% ---- 2023-09-17 ------------------------
# Function and class


class SignalMonitorWidget(pg.PlotWidget):
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('antialias', True)
    title = 'Main graph'

    def __init__(self):
        super().__init__()

        self.set_config()

        self.draw()

        LOGGER.debug(f'Initialized {self.__class__}')

    def set_config(self):
        self.setTitle(self.title)
        self.showGrid(x=True, y=True, alpha=0.5)

    def draw(self):
        self.pen1 = self.mkPen(color='#0000a0a0', width=1)
        self.curve1 = self.plot([], [], pen=self.pen1)

        self.pen2 = self.mkPen(color='red', width=5)
        self.curve2 = self.plot([], [], pen=self.pen2)

        LOGGER.debug(
            f'Initialized drawing of {self.curve1} ({self.pen1}), {self.curve2} ({self.pen2}).')

    def update1(self, pairs):
        ys = [e[0] for e in pairs]
        ts = [e[-1] for e in pairs]
        self.curve1.setData(ts, ys)

    def update2(self, pairs_delay):
        ys = [e[0] for e in pairs_delay]
        ts = [e[-1] for e in pairs_delay]
        self.curve2.setData(ts, ys)

    def mkPen(self, **kwargs):
        return pg.mkPen(**kwargs)


class MyWidget(QtWidgets.QMainWindow):
    """My QT-6 Widget

    It is an automatically QT application.

    @update_chart(y) (method): Update the chart using the new value,
                               it append the new point to the right-most point,
                               and it pop out the first point in the left-most end.

    @_add_series() (private method): Add a series to the chart.

    """

    window_length_seconds = CONF['display']['window_length_seconds']
    window_length_pnts = CONF['display']['window_length_seconds'] * \
        CONF['device']['sample_rate']
    window_title = 'Signal monitor'

    def __init__(self):
        # super(MyWidget, self).__init__()
        super().__init__()

        self.setWindowTitle(self.window_title)

        # --------------------------------------------------------------------------------
        # Hello world slogan and click method
        self.hello = ["Hello world", "Hallo Welt", "你好",
                      "Hei maailma", "Hola Mundo", "Привет мир"]

        self.button = QtWidgets.QPushButton("Click me!")
        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.button.clicked.connect(self.magic)

        # --------------------------------------------------------------------------------
        self.signal_monitor_widget = SignalMonitorWidget()

        # --------------------------------------------------------------------------------
        self.widget_0 = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_0)

        self.widget_0_0 = QtWidgets.QWidget()
        self.widget_0_1 = QtWidgets.QWidget()
        self.widget_0_2 = QtWidgets.QWidget()

        # --------------------------------------------------------------------------------
        # Make layout 0
        layout = QtWidgets.QHBoxLayout(self.widget_0)
        layout.addWidget(self.widget_0_0)
        layout.addWidget(self.widget_0_1)
        layout.addWidget(self.widget_0_2)

        # Make layout 0 0
        layout = QtWidgets.QVBoxLayout(self.widget_0_0)
        layout.addWidget(self.text)
        layout.addWidget(self.button)
        layout.addWidget(self.signal_monitor_widget)

        # Make layout 0 1
        layout = QtWidgets.QVBoxLayout(self.widget_0_1)
        self.subject_stuff(layout)

        # Make layout 0 2
        layout = QtWidgets.QVBoxLayout(self.widget_0_2)
        self.experiment_stuff(layout)

    @QtCore.Slot()
    def magic(self):
        self.text.setText(random.choice(self.hello))

    def experiment_stuff(self, layout):
        inputs = dict(
            predefined=QtWidgets.QComboBox(),
            seconds=QtWidgets.QLineEdit(),
            real=QtWidgets.QPushButton('Real'),
            fake=QtWidgets.QPushButton('Fake'),
            empty=QtWidgets.QPushButton('Empty'),
            repeat=QtWidgets.QPushButton('Repeat'),
            clear=QtWidgets.QPushButton('Clear'),
            refresh=QtWidgets.QPushButton('Refresh'),
            _summary=QtWidgets.QTextEdit(),
            _buffer=[]
        )

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox('Experiment setup')
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel('Predefined protocols'))
        vbox.addWidget(inputs['predefined'])
        inputs['predefined'].addItems([
            '---- (Begin from zero)',
            'Protocol 1 (Single block)',
            'Protocol 2 (Alternating blocks)'
        ])

        def _change_protocol():
            protocol = inputs['predefined'].currentText()
            print(protocol)

            if protocol.startswith('----'):
                _clear()

            if protocol.startswith('Protocol 1'):
                _clear()
                inputs['_buffer'] = [
                    ('Real', 60),
                ]

            if protocol.startswith('Protocol 2'):
                _clear()
                inputs['_buffer'] = [
                    ('Real', 60),
                    ('Fake', 60),
                    ('Real', 60),
                    ('Fake', 60),
                    ('Real', 60),
                    ('Fake', 60),
                    ('Real', 60),
                    ('Fake', 60),
                ]

            _update_summary()

        inputs['predefined'].currentTextChanged.connect(_change_protocol)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel('Block length (seconds):'))
        vbox.addWidget(inputs['seconds'])
        inputs['seconds'].setValidator(QIntValidator())
        inputs['seconds'].setText('60')

        # --------------------------------------------------------------------------------
        widget = QtWidgets.QWidget()
        vbox.addWidget(widget)
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)
        hbox.addWidget(inputs['real'])
        hbox.addWidget(inputs['fake'])
        hbox.addWidget(inputs['empty'])

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel('Summary:'))
        vbox.addWidget(inputs['_summary'])

        # --------------------------------------------------------------------------------
        widget = QtWidgets.QWidget()
        vbox.addWidget(widget)
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)

        hbox.addWidget(inputs['repeat'])
        hbox.addWidget(inputs['clear'])
        hbox.addWidget(inputs['refresh'])

        # --------------------------------------------------------------------------------
        def _update_summary():
            n = 0
            length = 0
            text = []
            for type, value in inputs['_buffer']:
                n += 1
                length += value
                text.append(f'{n:03d}: {type}\t: {value}\t: {length}')

            text = ['# Automatic generated task design',
                    f'# Blocks: {n}',
                    f'# Costs: {length} seconds',
                    '',
                    '# Real: Block with real feedback',
                    '# Fake: Block with fake feedback',
                    '# Empty: Block with empty screen',
                    '',
                    'Idx: Type\t: Block\t: Total'] + text

            return inputs['_summary'].setText('\n'.join(text))

        def _clear():
            inputs['_buffer'] = []
            _update_summary()

        def _repeat():
            inputs['_buffer'] += inputs['_buffer']
            _update_summary()

        def _add_block(block):
            seconds = int(inputs['seconds'].text())
            inputs['_buffer'].append((block, seconds))
            _update_summary()

        def _add_block_real():
            _add_block('real')

        def _add_block_fake():
            _add_block('fake')

        def _add_block_empty():
            _add_block('empty')

        inputs['clear'].clicked.connect(_clear)
        inputs['repeat'].clicked.connect(_repeat)
        inputs['refresh'].clicked.connect(_update_summary)

        inputs['real'].clicked.connect(_add_block_real)
        inputs['fake'].clicked.connect(_add_block_fake)
        inputs['empty'].clicked.connect(_add_block_empty)

        _clear()

        return inputs

    def subject_stuff(self, layout):
        inputs = dict(
            date=QtWidgets.QDateTimeEdit(),
            subject=QtWidgets.QLineEdit(),
            gender=QtWidgets.QComboBox(),
            age=QtWidgets.QDial(),
            _summary=QtWidgets.QTextEdit()
        )

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox('Subject setup')
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel('Date:'))
        vbox.addWidget(inputs['date'])
        inputs['date'].setDateTime(QtCore.QDateTime.currentDateTime())

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel('Subject:'))
        vbox.addWidget(inputs['subject'])
        inputs['subject'].setPlaceholderText('Subject name')

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel('Gender:'))
        inputs['gender'].addItems(['male', 'female'])
        vbox.addWidget(inputs['gender'])

        # --------------------------------------------------------------------------------
        ql = QtWidgets.QLabel('Age:')
        vbox.addWidget(ql)

        inputs['age'].setRange(1, 40)
        inputs['age'].setSingleStep(1)

        def callback(v):
            ql.setText(f'Age: {v}')

        inputs['age'].valueChanged.connect(callback)
        inputs['age'].setValue(7)
        vbox.addWidget(inputs['age'])

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel('Summary:'))
        vbox.addWidget(inputs['_summary'])

        # --------------------------------------------------------------------------------
        def onchange():
            text = '\n'.join([
                f"Date: {inputs['date'].dateTime().toString()}",
                f"Subject: {inputs['subject'].text()}",
                f"Gender: {inputs['gender'].currentText()}",
                f"Age: {inputs['age'].value()}",
            ])
            inputs['_summary'].setText(text)

        inputs['date'].dateTimeChanged.connect(onchange)
        inputs['subject'].textChanged.connect(onchange)
        inputs['gender'].currentTextChanged.connect(onchange)
        inputs['age'].valueChanged.connect(onchange)

        onchange()

        return inputs

    def update_graph(self, pairs=None, pairs_delay=None):
        self.signal_monitor_widget.disableAutoRange()

        if pairs is not None:
            self.signal_monitor_widget.update1(pairs)

        if pairs_delay is not None:
            self.signal_monitor_widget.update2(pairs_delay)

        self.signal_monitor_widget.enableAutoRange()

        pass


# %% ---- 2023-09-17 ------------------------
# Play ground


# %% ---- 2023-09-17 ------------------------
# Pending


# %% ---- 2023-09-17 ------------------------
# Pending
