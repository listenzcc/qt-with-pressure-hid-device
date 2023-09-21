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
import json
import time
import random
import threading
import pyqtgraph as pg
from datetime import datetime

from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QFont
from PySide6.QtCore import QTranslator, QCoreApplication

from . import LOGGER, CONF, root
from .load_protocols import MyProtocol
from .real_time_hid_reader import RealTimeHidReader

from rich import inspect


# %% ---- 2023-09-17 ------------------------
# Function and class

def tr(key: str, context: str = 'default', **kwargs) -> str:
    """Translate key with context

    Args:
        key (str): The input key word;
        context (str, optional): The context of the translation. Defaults to 'default'.

    Returns:
        str: The translation.
    """
    output = QCoreApplication.translate(context, key, **kwargs)
    LOGGER.debug(f'Translated {key}({context}) = {output}')
    return output


class SignalMonitorWidget(pg.PlotWidget):
    """
    The pyqtgraph widget for high speed display
    """

    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    pg.setConfigOption('antialias', True)
    title = 'Main graph'
    max_value = CONF['display']['max_value']
    min_value = CONF['display']['min_value']
    ref_value = CONF['display']['ref_value']

    def __init__(self):
        super().__init__()

        self.set_config()

        self.place_components()

        LOGGER.debug(f'Initialized {self.__class__}')

    def set_config(self):
        """
        Init setup configures
        """
        self.setTitle(self.title)
        self.showGrid(x=True, y=True, alpha=0.5)
        self.disableAutoRange()
        self.setYRange(self.min_value, self.max_value)

    def ellipse4_size_changed(self, ref_value: float):
        """
        Callback for the size of ellipse4,
        the ellipse4 is the reference circle to be fitted.

        Args:
            ref_value (float): The reference value.
        """
        cx = (self.max_value + self.min_value) / 2
        cy = (self.max_value + self.min_value) / 2
        w = ref_value
        h = ref_value
        x = cx - w/2
        y = cy - h/2

        self.ref_value = ref_value

        self.ellipse4.setRect(x, y, w, h)

    def ellipse5_size_changed(self, value: float):
        """
        Callback for the size changing of ellipse5,
        the ellipse5 is the morphing circle controlled by the pressure.

        Args:
            value (float): The value of the input pressure.
        """
        cx = (self.max_value + self.min_value) / 2
        cy = (self.max_value + self.min_value) / 2

        r = 1 - 2 ** (-abs(value - self.ref_value) / self.ref_value)

        if value > self.ref_value:
            # The pressure is large, pitch the circle
            w = self.ref_value * (1+r)
            h = 2 * self.ref_value - w
        else:
            h = self.ref_value * (1+r)
            w = 2 * self.ref_value - h

        x = cx - w/2
        y = cy - h/2

        self.ellipse5.setRect(x, y, w, h)

    def place_components(self):
        """
        Place the display components on the figure.
        """
        # --------------------------------------------------------------------------------
        self.pen1 = pg.mkPen(color='blue')
        self.curve1 = self.plot([], [], pen=self.pen1)

        # --------------------------------------------------------------------------------
        self.pen2 = pg.mkPen(color='red')
        self.curve2 = self.plot([], [], pen=self.pen2)

        # --------------------------------------------------------------------------------
        self.pen3 = pg.mkPen(color='green')
        self.curve3 = self.plot([], [], pen=self.pen3)

        # --------------------------------------------------------------------------------
        self.pen4 = pg.mkPen(color='red', width=5)
        self.ellipse4 = QtWidgets.QGraphicsEllipseItem(
            1000-250, 1000-250, 500, 500)
        self.ellipse4.setPen(self.pen4)
        self.addItem(self.ellipse4)

        # --------------------------------------------------------------------------------
        self.pen5 = pg.mkPen(color='black', width=3)
        self.ellipse5 = QtWidgets.QGraphicsEllipseItem(
            1000-250, 1000-250, 500, 500)
        self.ellipse5.setPen(self.pen5)
        self.addItem(self.ellipse5)

        # --------------------------------------------------------------------------------
        legend = self.getPlotItem().addLegend(offset=(10, 10))
        self.block_text = pg.TextItem('Idle')
        font = QFont()
        font.setPixelSize(40)
        self.block_text.setFont(font)
        self.block_text.setAnchor((0, 0))
        self.block_text.setFlag(
            self.block_text.GraphicsItemFlag.ItemIgnoresTransformations)
        self.block_text.setParentItem(legend)

        # --------------------------------------------------------------------------------
        self.status_text = pg.TextItem('--')
        font = QFont()
        font.setPixelSize(20)
        self.status_text.setFont(font)
        self.status_text.setAnchor((1, 0))
        self.status_text.setPos(self.width() - 80, 0)
        self.status_text.setFlag(
            self.status_text.GraphicsItemFlag.ItemIgnoresTransformations)
        self.status_text.setParentItem(legend)

        # --------------------------------------------------------------------------------
        legend.setZValue(-10000000)
        self.curve3.setZValue(1)
        self.curve1.setZValue(2)
        self.curve2.setZValue(3)

        LOGGER.debug(
            f'Initialized drawing of {self.curve1} ({self.pen1}), {self.curve2} ({self.pen2}).')

    def update_curve1(self, pairs):
        """
        Update the curve1 with the given pairs,
        the curve1 is the realtime pressure curve.

        Args:
            pairs (list): The array of realtime pressure curve,
                          the element is like (value,..., timestamp)
        """
        ys = [e[0] for e in pairs]
        ts = [e[-1] for e in pairs]
        self.curve1.setData(ts, ys)

    def update_curve2(self, pairs_delay):
        """
        Update the curve1 with the given pairs,
        the curve2 is the delayed pressure curve.

        Args:
            pairs_delay (list): The array of delayed pressure curve,
                                the element is like (value,..., timestamp)
        """
        ys = [e[0] for e in pairs_delay]
        ts = [e[-1] for e in pairs_delay]
        self.curve2.setData(ts, ys)

    def update_curve3(self, t0: float, t1: float, ref_value: float, flag: bool):
        """
        Update the curve3 with the ref_value,
        the curve3 is the horizontal line with the reference pressure value

        Args:
            t0 (float): The start timestamp;
            t1 (float): The stop timestamp;
            ref_value (float): The reference pressure;
            flag (bool): Whether to draw the straight line or draw nothing.
        """
        if flag:
            self.curve3.setData([t0, t1], [ref_value, ref_value])
        else:
            self.curve3.setData([], [])


class BlockManager(object):
    """
    The block manager
    @parse_blocks(blocks) is the built-in method to startup from the input blocks;
    @consume(t) is the method determine the current block and pop it if it is exceeded.
    """
    design = []

    def __init__(self, blocks=[]):
        self.design = self.parse_blocks(blocks)
        LOGGER.debug(f'Initialized {self.__class__}')

    def parse_blocks(self, blocks: list):
        """Parse the input block design

        Args:
            blocks (list): The list of blocks.

        Returns:
            list: rich information blocks.
        """
        design = []

        if len(blocks) == 0:
            LOGGER.debug('Parsed empty blocks.')
            return design

        design.append(dict(
            idx=0,
            name=blocks[0][0],
            duration=blocks[0][1],
            start=0,
            stop=blocks[0][1],
        ))

        for block in blocks[1:]:
            idx = len(design)
            duration = block[1]
            start = design[-1]['stop']
            stop = start + duration

            design.append(dict(
                idx=idx,
                name=block[0],
                duration=duration,
                start=start,
                stop=stop
            ))

        for d in design:
            d['total'] = stop
            d['blocks'] = idx+1

        LOGGER.debug(f'Parsed blocks design: {design}')

        return design

    def consume(self, t: float):
        """Consume the block if necessary

        ** Consumed all the blocks ** is a very special output,
        it refers the blocks end, and it is a once for all output, never repeated.

        Args:
            t (float): The time from blocks beginning.

        Returns:
            str or dict: dict refers the dict,
                         str refers the blocks are empty,
                        * No block at all: The block design is empty, it refers nothing is running and abnormal;
                        * Consumed all the blocks: The block design is currently finished, it refers the experiment closes correctly,
                          it calls for experiment stopping workload, like saving data or something like that.
        """

        if len(self.design) == 0:
            return 'No block at all.'

        if t > self.design[0]['stop']:
            d = self.design.pop(0)
            LOGGER.debug(f'Consumed block {d}')

        if len(self.design) == 0:
            return 'Consumed all the blocks.'

        return self.design[0]


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
    delay_seconds = CONF['display']['delay_seconds']

    ref_value = CONF['display']['ref_value']
    max_value = CONF['display']['max_value']
    min_value = CONF['display']['min_value']
    display_ref_flag = CONF['display']['display_ref_flag']

    display_mode = 'Realtime'
    display_modes = ['Realtime', 'Delayed', 'Circle fit']

    window_title = 'Pressure feedback system by Dr. Zhang'

    device_reader = None
    timer = None
    block_manager = BlockManager()
    my_protocol = MyProtocol()
    data_folder_path = root.joinpath('Data')

    def __init__(self):
        # super(MyWidget, self).__init__()
        super().__init__()

        # --------------------------------------------------------------------------------
        # Hello world slogan and click method
        self.hello = ["Hello world", "Hallo Welt", "你好",
                      "Hei maailma", "Hola Mundo", "Привет мир"]

        self.start_button = QtWidgets.QPushButton(tr("Start"))
        self.terminate_button = QtWidgets.QPushButton(tr("Terminate"))

        self.text = QtWidgets.QLabel("Hello World",
                                     alignment=QtCore.Qt.AlignCenter)

        self.start_button.clicked.connect(self.magic)
        self.terminate_button.clicked.connect(self.terminate)
        self.terminate_button.setDisabled(True)

        # --------------------------------------------------------------------------------
        self.signal_monitor_widget = SignalMonitorWidget()

        # --------------------------------------------------------------------------------
        self.widget_0 = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_0)

        self.widget_0_0 = QtWidgets.QWidget()
        self.widget_0_1 = QtWidgets.QWidget()
        self.widget_0_2 = QtWidgets.QWidget()
        self.widget_0_3 = QtWidgets.QWidget()

        # --------------------------------------------------------------------------------
        # Make layout 0
        layout = QtWidgets.QHBoxLayout(self.widget_0)
        layout.addWidget(self.widget_0_3)
        layout.addWidget(self.widget_0_0)
        layout.addWidget(self.widget_0_1)
        layout.addWidget(self.widget_0_2)

        # Make layout 0 0
        layout = QtWidgets.QVBoxLayout(self.widget_0_0)
        layout.addWidget(self.text)
        widget = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.terminate_button)
        layout.addWidget(widget)
        layout.addWidget(self.signal_monitor_widget)

        # Make layout 0 1
        layout = QtWidgets.QVBoxLayout(self.widget_0_1)
        self.subject_inputs = self.subject_stuff(layout)

        # Make layout 0 2
        layout = QtWidgets.QVBoxLayout(self.widget_0_2)
        self.experiment_inputs = self.experiment_stuff(layout)

        # Make layout 0 3
        layout = QtWidgets.QVBoxLayout(self.widget_0_3)
        self.display_inputs = self.display_stuff(layout)

    def link_reader(self, reader: RealTimeHidReader):
        """
        Link to the hid device reader.

        Args:
            reader (RealTimeHidReader): _description_
        """

        if self.device_reader is not None:
            pairs = self.device_reader.stop()
            time.sleep(0.1)
            LOGGER.warning(
                f'Closed existing device reader, discharging {len(pairs)} pnts data')

        reader.delay_seconds = self.delay_seconds

        self.device_reader = reader

        reader.start()

        LOGGER.debug(f'Linked with device reader: {reader}')

        self.setWindowTitle(tr(self.window_title))

        if self.timer is not None:
            self.timer.stop()
            LOGGER.warning(f'Stopped existing timer {self.timer}')

        n = int(self.window_length_seconds * reader.sample_rate)
        nd = int(reader.sample_rate *
                 (self.window_length_seconds - self.delay_seconds))

        def update():
            pairs = reader.peek(n)
            pairs_delay = reader.peek(nd, peek_delay=True)
            self.update_graph(pairs, pairs_delay)

        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start()

        self.timer = timer

    @QtCore.Slot()
    def terminate(self):
        """Terminate the current block design experiment.
        """
        self.block_manager = BlockManager()
        self.start_button.setDisabled(False)
        self.terminate_button.setDisabled(True)
        LOGGER.debug(
            'Terminated block designed experiment, and the start_button disable status is released.')

    @QtCore.Slot()
    def magic(self):
        """
        Start the block design experiment form the current setup.

        It also restarts the self.device_reader.
        """
        self.text.setText(random.choice(self.hello))

        self.start_button.setDisabled(True)
        self.terminate_button.setDisabled(False)

        self.block_manager = BlockManager(self.experiment_inputs['_buffer'])

        if len(self.block_manager.design) == 0:
            self.start_button.setDisabled(False)
            self.terminate_button.setDisabled(True)
            LOGGER.warning(
                'Tried to start the block designed experiment, but no design was found.')
            return

        # Snapshot the current setup.
        self.setup_snapshot = dict(
            subject_info=self.subject_inputs['_summary'].toPlainText(),
            experiment_info=self.experiment_inputs['_buffer']
        )

        self.device_reader.stop()
        # time.sleep(1)
        self.device_reader.start()

    def save_data(self):
        """
        Save the data and the snapshot setup for the block design experiment.

        It also restarts the self.device_reader.
        """
        data = self.device_reader.stop()

        subject_info = self.setup_snapshot['subject_info']
        experiment_info = self.setup_snapshot['experiment_info']

        folder = self.data_folder_path.joinpath(
            '{}'.format(datetime.strftime(datetime.now(), '%Y-%m-%d-%H-%M-%S')))

        folder.mkdir(exist_ok=True, parents=True)

        json.dump(data, open(folder.joinpath('data.json'), 'w'))
        json.dump(subject_info, open(folder.joinpath('subject.json'), 'w'))
        json.dump(experiment_info, open(
            folder.joinpath('experiment.json'), 'w'))

        LOGGER.debug(f'Saved data into {folder}')

        self.start_button.setDisabled(False)
        self.terminate_button.setDisabled(True)

        self.device_reader.start()

    def display_stuff(self, layout: QtWidgets.QVBoxLayout) -> dict:
        """
        Place the display stuff components to the widget,
        with the given layout.

        Args:
            layout (QtWidgets.QVBoxLayout): The input layout

        Returns:
            dict: The necessary widgets of inputs
        """
        def _tr(s):
            return tr(s, 'display setup session')

        inputs = dict(
            line1_color=QtWidgets.QPushButton('    '),
            line1_width=QtWidgets.QSpinBox(),
            line2_color=QtWidgets.QPushButton('    '),
            line2_width=QtWidgets.QSpinBox(),
            line2_delay=QtWidgets.QSpinBox(),
            line3_color=QtWidgets.QPushButton('    '),
            line3_width=QtWidgets.QSpinBox(),
            line3_ref_value=QtWidgets.QDial(),
            zone3=QtWidgets.QGroupBox(_tr('Ref. value')),
            display_mode=QtWidgets.QComboBox(),
            button_0g=QtWidgets.QPushButton(_tr('Correction 0g')),
            button_200g=QtWidgets.QPushButton(_tr('Correction 200g')),
        )

        def pen2hex(pen):
            rgb = list(pen.color().toTuple())[:3]
            string = '#' + ''.join([hex(e).replace('x', '')[-2:] for e in rgb])
            return string

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox(_tr('Display setup'))
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        # --------------------------------------------------------------------------------
        inputs['display_mode'].addItems(self.display_modes)
        inputs['display_mode'].setCurrentText(self.display_mode)

        vbox.addWidget(inputs['display_mode'])

        # --------------------------------------------------------------------------------
        zone1 = QtWidgets.QGroupBox(_tr('Curve (realtime)'))
        vbox.addWidget(zone1)
        vbox1 = QtWidgets.QVBoxLayout()
        zone1.setLayout(vbox1)

        hbox = QtWidgets.QHBoxLayout()
        vbox1.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr('Color')))
        hbox.addWidget(inputs['line1_color'])

        hbox = QtWidgets.QHBoxLayout()
        vbox1.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr('Width')))
        hbox.addWidget(inputs['line1_width'])

        inputs['line1_width'].setValue(2)
        inputs['line1_width'].setMinimum(1)
        inputs['line1_width'].setMaximum(10)

        # --------------------------------------------------------------------------------
        zone2 = QtWidgets.QGroupBox(_tr('Curve (delay)'))
        vbox.addWidget(zone2)
        vbox2 = QtWidgets.QVBoxLayout()
        zone2.setLayout(vbox2)

        hbox = QtWidgets.QHBoxLayout()
        vbox2.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr('Delay (seconds)')))
        hbox.addWidget(inputs['line2_delay'])

        hbox = QtWidgets.QHBoxLayout()
        vbox2.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr('Color')))
        hbox.addWidget(inputs['line2_color'])

        hbox = QtWidgets.QHBoxLayout()
        vbox2.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr('Width')))
        hbox.addWidget(inputs['line2_width'])

        inputs['line2_width'].setValue(2)
        inputs['line2_width'].setMinimum(1)
        inputs['line2_width'].setMaximum(10)

        # --------------------------------------------------------------------------------
        inputs['line2_delay'].setValue(10)
        inputs['line2_delay'].setMinimum(1)
        inputs['line2_delay'].setMaximum(10)

        def _change_delay(delay):
            self.delay_seconds = delay
            self.link_reader(self.device_reader)
            pass

        inputs['line2_delay'].valueChanged.connect(_change_delay)

        # --------------------------------------------------------------------------------
        zone3 = inputs['zone3']
        zone3.setCheckable(True)
        vbox.addWidget(zone3)
        vbox3 = QtWidgets.QVBoxLayout()
        zone3.setLayout(vbox3)

        hbox = QtWidgets.QHBoxLayout()
        vbox3.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr('Color')))
        hbox.addWidget(inputs['line3_color'])

        hbox = QtWidgets.QHBoxLayout()
        vbox3.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr('Width')))
        hbox.addWidget(inputs['line3_width'])

        hbox = QtWidgets.QHBoxLayout()
        vbox3.addLayout(hbox)

        hbox.addWidget(QtWidgets.QLabel(_tr('Ref. value')))
        label = QtWidgets.QLabel('500')
        hbox.addWidget(label)

        vbox3.addWidget(inputs['line3_ref_value'])

        inputs['line3_width'].setValue(2)
        inputs['line3_width'].setMinimum(1)
        inputs['line3_width'].setMaximum(10)

        inputs['line3_ref_value'].setValue(500)
        inputs['line3_ref_value'].setMinimum(1)
        inputs['line3_ref_value'].setMaximum(2000)

        def _change_ref_value(v):
            self.ref_value = v
            self.signal_monitor_widget.ellipse4_size_changed(v)
            label.setText('{}'.format(v))

        inputs['line3_ref_value'].valueChanged.connect(_change_ref_value)

        def _check_zone3(b):
            self.display_ref_flag = b

        zone3.toggled.connect(_check_zone3)

        # --------------------------------------------------------------------------------
        zone4 = QtWidgets.QGroupBox(_tr('Correction'))
        zone4.setCheckable(True)
        zone4.setChecked(False)
        vbox.addWidget(zone4)
        vbox4 = QtWidgets.QVBoxLayout()
        zone4.setLayout(vbox4)

        vbox4.addWidget(inputs['button_0g'])
        vbox4.addWidget(inputs['button_200g'])

        def _write_to_correction(real_g, num):
            p = root.joinpath(f'correction/g{real_g}')
            with open(p, 'w') as f:
                f.write(f'{num}')
            LOGGER.debug(f'Wrote correction {real_g}({num}) to {p}')

        def _correction_0g():
            pairs = self.device_reader.peek(100)

            n = len(pairs)

            if n == 0:
                LOGGER.debug(
                    'Failed to correct with the 0 g, since the data is empty')
                return

            g0 = int(sum([e[1] for e in pairs]) / n)
            self.device_reader.g0 = g0

            threading.Thread(target=_write_to_correction, args=(0, g0)).start()

            LOGGER.debug(f'Re-correct the g0 to {g0} (with {n} points)')

        def _correction_200g():
            pairs = self.device_reader.peek(100)

            n = len(pairs)

            if n == 0:
                LOGGER.debug(
                    'Failed to correct with the 200 g, since the data is empty')
                return

            g200 = int(sum([e[1] for e in pairs]) / n)
            self.device_reader.g200 = g200

            threading.Thread(target=_write_to_correction,
                             args=(200, g200)).start()

            LOGGER.debug(f'Re-correct the g200 to {g200} (with {n} points)')

        inputs['button_0g'].clicked.connect(_correction_0g)
        inputs['button_200g'].clicked.connect(_correction_200g)

        # --------------------------------------------------------------------------------

        def _fit_color1():
            inputs['line1_color'].setStyleSheet(
                'QPushButton {background-color: ' + pen2hex(self.signal_monitor_widget.pen1) + '}')

        def _change_color1():
            qColor = QtWidgets.QColorDialog(self).getColor(
                self.signal_monitor_widget.pen1.color())

            if not qColor.isValid():
                return

            self.signal_monitor_widget.pen1.setColor(qColor)
            _fit_color1()

            LOGGER.debug(f'Set line1 color to: {qColor}')

        def _change_width1(width):
            self.signal_monitor_widget.pen1.setWidth(width)

        _fit_color1()
        _change_width1(2)

        inputs['line1_color'].clicked.connect(_change_color1)
        inputs['line1_width'].valueChanged.connect(_change_width1)

        # --------------------------------------------------------------------------------
        def _fit_color2():
            inputs['line2_color'].setStyleSheet(
                'QPushButton {background-color: ' + pen2hex(self.signal_monitor_widget.pen2) + '}')

        def _change_color2():
            qColor = QtWidgets.QColorDialog(self).getColor(
                self.signal_monitor_widget.pen2.color())

            if not qColor.isValid():
                return

            self.signal_monitor_widget.pen2.setColor(qColor)
            _fit_color2()

            LOGGER.debug(f'Set line2 color to: {qColor}')

        def _change_width2(width):
            self.signal_monitor_widget.pen2.setWidth(width)

        _fit_color2()
        _change_width2(2)

        inputs['line2_color'].clicked.connect(_change_color2)
        inputs['line2_width'].valueChanged.connect(_change_width2)

        # --------------------------------------------------------------------------------
        def _fit_color3():
            inputs['line3_color'].setStyleSheet(
                'QPushButton {background-color: ' + pen2hex(self.signal_monitor_widget.pen3) + '}')

        def _change_color3():
            qColor = QtWidgets.QColorDialog(self).getColor(
                self.signal_monitor_widget.pen3.color())

            if not qColor.isValid():
                return

            self.signal_monitor_widget.pen3.setColor(qColor)
            _fit_color3()

            LOGGER.debug(f'Set line3 color to: {qColor}')

        def _change_width3(width):
            self.signal_monitor_widget.pen3.setWidth(width)

        _fit_color3()
        _change_width3(2)

        inputs['line3_color'].clicked.connect(_change_color3)
        inputs['line3_width'].valueChanged.connect(_change_width3)

        # --------------------------------------------------------------------------------
        def _change_display_mode(mode):
            self.display_mode = mode

            if mode == 'Realtime':
                zone1.setVisible(True)
                zone2.setVisible(False)
                zone3.setVisible(True)

            if mode == 'Delayed':
                zone1.setVisible(True)
                zone2.setVisible(True)
                zone3.setVisible(True)

        inputs['display_mode'].currentTextChanged.connect(_change_display_mode)
        _change_display_mode(self.display_mode)

        return inputs

    def experiment_stuff(self, layout: QtWidgets.QVBoxLayout) -> dict:
        """
        Place the experiment stuff components to the widget,
        with the given layout.

        Args:
            layout (QtWidgets.QVBoxLayout): The input layout

        Returns:
            dict: The necessary widgets of inputs
        """
        def _tr(s):
            return tr(s, 'experiment setup session')

        inputs = dict(
            predefined=QtWidgets.QComboBox(),
            seconds=QtWidgets.QSpinBox(),
            real=QtWidgets.QPushButton(_tr('Real')),
            fake=QtWidgets.QPushButton(_tr('Fake')),
            empty=QtWidgets.QPushButton(
                _tr('Empty')),
            repeat=QtWidgets.QPushButton(
                _tr('Repeat')),
            clear=QtWidgets.QPushButton(
                _tr('Clear')),
            refresh=QtWidgets.QPushButton(
                _tr('Refresh')),
            save=QtWidgets.QPushButton(_tr('Save')),
            _summary=QtWidgets.QTextEdit(),
            _buffer=[]
        )

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox(
            _tr('Experiment setup'))
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(
            _tr('Predefined protocols')))
        vbox.addWidget(inputs['predefined'])

        for k, v in self.my_protocol.protocols.items():
            txt = f'{k} | {v.get("name", "")}'
            inputs['predefined'].addItems([txt])

        def _change_protocol():
            protocol = inputs['predefined'].currentText()
            k = protocol.split(' | ')[0]
            _clear()
            inputs['_buffer'] = self.my_protocol.get_buffer(k)
            _update_summary()

        inputs['predefined'].currentTextChanged.connect(_change_protocol)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(
            _tr('Block length (seconds)')))
        vbox.addWidget(inputs['seconds'])
        inputs['seconds'].setValue(10)
        inputs['seconds'].setMaximum(3600)
        inputs['seconds'].setMinimum(1)

        # --------------------------------------------------------------------------------
        widget = QtWidgets.QWidget()
        vbox.addWidget(widget)
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)
        hbox.addWidget(inputs['real'])
        hbox.addWidget(inputs['fake'])
        hbox.addWidget(inputs['empty'])

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr('Summary')))
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
        vbox.addWidget(inputs['save'])

        def _save():
            name, ok = QtWidgets.QInputDialog.getText(
                self, 'Save protocol', 'Description:')

            if ok:
                print(f'Saving {name}')
                self.my_protocol.save(name, inputs['_buffer'])

        inputs['save'].clicked.connect(_save)

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

    def subject_stuff(self, layout: QtWidgets.QVBoxLayout) -> dict:
        """
        Place the subject stuff components to the widget,
        with the given layout.

        Args:
            layout (QtWidgets.QVBoxLayout): The input layout

        Returns:
            dict: The necessary widgets of inputs
        """
        def _tr(s):
            return tr(s, 'subject setup session')

        inputs = dict(
            date=QtWidgets.QDateTimeEdit(),
            subject=QtWidgets.QLineEdit(),
            gender=QtWidgets.QComboBox(),
            age=QtWidgets.QDial(),
            _summary=QtWidgets.QTextEdit()
        )

        def _tr(s):
            return tr(s, 'subject setup session')

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox(_tr('Subject setup'))
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr('Experiment date')))
        vbox.addWidget(inputs['date'])
        inputs['date'].setDateTime(QtCore.QDateTime.currentDateTime())

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr('Subject name')))
        vbox.addWidget(inputs['subject'])
        inputs['subject'].setPlaceholderText(_tr('Subject name'))

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr('Subject gender')))
        inputs['gender'].addItems([_tr('male'), _tr('female')])
        vbox.addWidget(inputs['gender'])

        # --------------------------------------------------------------------------------
        ql = QtWidgets.QLabel(_tr('Subject age'))
        vbox.addWidget(ql)

        inputs['age'].setRange(1, 40)
        inputs['age'].setSingleStep(1)

        def callback(v):
            ql.setText('{}: {}'.format(_tr('Subject age'), v))  # f'Age: {v}')

        inputs['age'].valueChanged.connect(callback)
        inputs['age'].setValue(7)
        vbox.addWidget(inputs['age'])

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr('Summary')))
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

    def update_signal_experiment_status(self, pairs: list):
        """
        Update the status for the signal collecting and experiment block.

        Args:
            pairs (list): The incoming new data.

        Returns:
            None: None refers the pairs is invalid;
            (t0, t1, block_name):
            t0: The start time of the new data;
            t1: The end time of the new data;
            block_name: The current block name, empty string for not important block name.
        """
        if pairs is None:
            return

        if len(pairs) == 0:
            return

        t0 = pairs[0][-1]
        t1 = pairs[-1][-1]

        n = len(pairs)-1
        # r = int(n/(t1 - t0)+0.5)
        r = n/max(t1 - t0, 1e-4)
        self.signal_monitor_widget.status_text.setText(
            f'{r:.2f} Hz')

        block = self.block_manager.consume(t1)

        if block == 'Consumed all the blocks.':
            self.signal_monitor_widget.block_text.setText(
                'Finished')
            LOGGER.debug('Block design is completed.')
            self.save_data()
            return

        if block == 'No block at all.':
            self.signal_monitor_widget.block_text.setText(
                f'Idle {pairs[-1][0]:.2f}')
            return t0, t1, ''

        if isinstance(block, dict):
            block_name = block['name']
            stop = block['stop']
            total = block['total']

            txt = f'{block_name} | {stop-t1:.0f} | {total-t1:.0f}'

            self.signal_monitor_widget.block_text.setText(txt)

        return t0, t1, block_name

    def update_curve13(self, pairs: list, t0: float, t1: float, block_name: str, expand_t: float = 0):
        """
        Update the curve1 (the realtime curve) and curve3 (the reference line) in the signal displaying widget (the pyqtgraph figure)

        Args:
            pairs (list): The incoming new data;
            t0 (float): The start time of the new data;
            t1 (float): The end time of the new data;
            block_name (str): The block_name, it controls how the curve1 and curve3 is drawn;
            expand_t (float, optional): How many seconds the end time is expanded to the xRange. Defaults to 0.
        """
        self.signal_monitor_widget.setXRange(
            t0, max(t1, self.window_length_seconds) + expand_t, padding=0)

        if block_name == 'Empty':
            self.signal_monitor_widget.update_curve1([])
            self.signal_monitor_widget.update_curve3(0, 0, 0, False)
        else:
            self.signal_monitor_widget.update_curve1(pairs)
            self.signal_monitor_widget.update_curve3(
                t0,
                max(t1, self.window_length_seconds) + expand_t,
                self.ref_value,
                self.display_ref_flag)

    def update_curve2(self, pairs_delay: list):
        """
        Update the curve2 (the delayed curve)

        Args:
            pairs_delay (list): The delayed mean value of the incoming new data.
        """
        if pairs_delay is None:
            return

        self.signal_monitor_widget.update_curve2(pairs_delay)

    def toggle_displays(self):
        """
        Setup visible value for the curves according to the current self.display_mode
        """
        if self.display_mode == 'Delayed':
            self.signal_monitor_widget.curve1.setVisible(True)
            self.signal_monitor_widget.curve2.setVisible(True)
            self.signal_monitor_widget.curve3.setVisible(
                self.display_inputs['zone3'].isChecked())
            self.signal_monitor_widget.ellipse4.setVisible(False)
            self.signal_monitor_widget.ellipse5.setVisible(False)

        if self.display_mode == 'Realtime':
            self.signal_monitor_widget.curve1.setVisible(True)
            self.signal_monitor_widget.curve2.setVisible(False)
            self.signal_monitor_widget.curve3.setVisible(
                self.display_inputs['zone3'].isChecked())
            self.signal_monitor_widget.ellipse4.setVisible(False)
            self.signal_monitor_widget.ellipse5.setVisible(False)

        if self.display_mode == 'Circle fit':
            self.signal_monitor_widget.curve1.setVisible(False)
            self.signal_monitor_widget.curve2.setVisible(False)
            self.signal_monitor_widget.curve3.setVisible(False)
            self.signal_monitor_widget.ellipse4.setVisible(True)
            self.signal_monitor_widget.ellipse5.setVisible(True)

    def update_graph(self, pairs: list = None, pairs_delay: list = None):
        """
        Update the graph as the very fast loop

        Args:
            pairs (list, optional): The incoming data from the hid device. Defaults to None.
            pairs_delay (list, optional): The delayed mean of the incoming data from th hid device. Defaults to None.
        """
        current_block = self.update_signal_experiment_status(pairs)

        if current_block is None:
            return

        self.toggle_displays()

        t0, t1, block_name = current_block

        if self.display_mode == 'Delayed':
            self.update_curve13(pairs, t0, t1, block_name)

            if not block_name == 'Empty':
                self.update_curve2(pairs_delay)

        if self.display_mode == 'Realtime':
            self.update_curve13(pairs, t0, t1, block_name,
                                expand_t=self.window_length_seconds)

        if self.display_mode == 'Circle fit':
            self.signal_monitor_widget.setXRange(self.signal_monitor_widget.min_value,
                                                 self.signal_monitor_widget.max_value)
            if pairs is not None:
                if len(pairs) > 0:
                    self.signal_monitor_widget.ellipse5_size_changed(
                        pairs[-1][0])

        return


# %% ---- 2023-09-17 ------------------------
# Play ground


# %% ---- 2023-09-17 ------------------------
# Pending


# %% ---- 2023-09-17 ------------------------
# Pending
