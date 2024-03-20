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
import numpy as np

from pathlib import Path
from datetime import datetime
from threading import Thread

from PySide2.QtWidgets import QApplication
import pyqtgraph as pg
from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import QFont
from PySide2.QtCore import QCoreApplication

from . import LOGGER, CONF, root_path
from .load_protocols import MyProtocol
from .real_time_hid_reader import RealTimeHidReader
from .score_animation import ScoreAnimation, pil2rgb

from rich import print, inspect

# ---------------
sa = ScoreAnimation()
sa.reset()
sa.mk_frames()

app = QtWidgets.QApplication([])  # noqa

# %% ---- 2023-09-17 ------------------------
# Function and class


def tr(key: str, context: str = "default", **kwargs) -> str:
    """Translate key with context

    Args:
        key (str): The input key word;
        context (str, optional): The context of the translation. Defaults to 'default'.

    Returns:
        str: The translation.
    """
    output = QCoreApplication.translate(context, key, **kwargs)
    LOGGER.debug(f"Translated {key}({context}) = {output}")
    return output


class SignalMonitorWidget(pg.PlotWidget):
    """
    The pyqtgraph widget for high speed display
    """

    pg.setConfigOption("background", "w")
    pg.setConfigOption("foreground", "k")
    pg.setConfigOption("antialias", True)
    title = ""  # "Main graph"
    max_value = CONF["display"]["max_value"]
    min_value = CONF["display"]["min_value"]
    ref_value = CONF["display"]["ref_value"]

    def __init__(self):
        super().__init__()
        self.set_config()
        self.place_components()
        LOGGER.debug(f"Initialized {self.__class__}")

    def set_config(self):
        """
        Init setup configures
        """
        self.setTitle(self.title)
        self.disableAutoRange()
        self.enter_curve_mode()

    def enter_curve_mode(self, ref_value: float = None, x_grid: bool = True, y_grid: bool = True):
        """
        Sets the curve mode of the widget.

        Args:
            self: The instance of the widget.

        Returns:
            None
        """

        self.showGrid(x=x_grid, y=y_grid, alpha=0.5)
        if ref_value is None:
            self.setYRange(self.min_value, self.max_value)
        else:
            self.setYRange(self.min_value, ref_value*2)

    def animation_mode(self):
        self.showGrid(x=False, y=False)
        self.setXRange(0, sa.width, padding=0)
        self.setYRange(0, sa.height, padding=0)

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
        x = cx - w / 2
        y = cy - h / 2

        self.ref_value = ref_value

        self.ellipse4.setRect(x, y, w, h)

    def ellipse5_size_changed(self, value: float):
        """
        Updates the size and position of `ellipse5` based on the provided value.

        This method calculates the new size and position of `ellipse5` based on the given value.
        It uses the `ref_value` and `min_value` attributes to determine the scaling factor and adjusts the width and height accordingly.
        The resulting rectangle is then set as the new rectangle for `ellipse5`.

        Args:
            self: The object instance.
            value (float): The value used to calculate the size and position of `ellipse5`.

        Returns:
            None

        Example:
            ```python
            widget = WidgetClass()
            widget.ellipse5_size_changed(0.5)
            ```
        """

        cx = (self.max_value + self.min_value) / 2
        cy = (self.max_value + self.min_value) / 2

        r = 1 - 2 ** (-abs(value - self.ref_value) / self.ref_value)

        if value > self.ref_value:
            # The pressure is large, pitch the circle
            w = self.ref_value * (1 + r)
            h = 2 * self.ref_value - w
        else:
            h = self.ref_value * (1 + r)
            w = 2 * self.ref_value - h

        x = cx - w / 2
        y = cy - h / 2

        self.ellipse5.setRect(x, y, w, h)

    def place_components(self):
        """
        Places components on the widget for drawing.

        This method initializes and sets up various components for drawing on the widget.
        It creates and configures multiple curves, ellipses, and text items.
        The curves are associated with different pens, and the ellipses are positioned and styled with specific pens.
        The text items are set with custom fonts, positions, and parent items.
        The method also sets the z-order of the components and logs a debug message.

        Args:
            self: The object instance.

        Returns:
            None

        Example:
            ```python
            widget = WidgetClass()
            widget.place_components()
            ```
        """

        # --------------------------------------------------------------------------------
        # The curves of the pressure values (curve1 and curve2(delay)),
        # and the reference pressure value (curve3)
        self.pen1 = pg.mkPen(color="blue")
        self.curve1 = self.plot([], [], pen=self.pen1)

        self.pen2 = pg.mkPen(color="red")
        self.curve2 = self.plot([], [], pen=self.pen2)

        self.pen3 = pg.mkPen(color="green")
        self.curve3 = self.plot([], [], pen=self.pen3)

        # --------------------------------------------------------------------------------
        # The ellipse of pressure value response,
        # the ellipse4 is the under-pressure circle,
        # the ellipse5 is the reference circle.
        self.pen4 = pg.mkPen(color="red", width=5)
        self.ellipse4 = QtWidgets.QGraphicsEllipseItem(
            1000 - 250, 1000 - 250, 500, 500)
        self.ellipse4.setPen(self.pen4)
        self.addItem(self.ellipse4)

        self.pen5 = pg.mkPen(color="black", width=3)
        self.ellipse5 = QtWidgets.QGraphicsEllipseItem(
            1000 - 250, 1000 - 250, 500, 500)
        self.ellipse5.setPen(self.pen5)
        self.addItem(self.ellipse5)

        # --------------------------------------------------------------------------------
        # The background image
        # # vb = pg.ViewBox()
        # # self.addItem(vb)
        # # imv = pg.ImageView(self, view=vb)
        # imv = pg.ImageView(self)
        # # imv.show()
        # imv.setImage(pil2rgb(sa.buffer[0]).transpose([2, 1, 0]))
        # self.setBackground(imv)

        self.animation_img = pg.ImageItem()
        self.addItem(self.animation_img)
        mat = pil2rgb(sa.img)
        self.animation_img.setImage(mat[::-1].transpose([1, 0, 2]))

        # --------------------------------------------------------------------------------
        # The block text on the left-top corner
        legend = self.getPlotItem().addLegend(offset=(10, 10))
        self.block_text = pg.TextItem("Idle")
        font = QFont()
        font.setPixelSize(40)
        self.block_text.setFont(font)
        self.block_text.setAnchor((0, 0))
        self.block_text.setFlag(
            self.block_text.GraphicsItemFlag.ItemIgnoresTransformations
        )
        self.block_text.setParentItem(legend)

        # --------------------------------------------------------------------------------
        # The status text on the right-top corner
        self.status_text = pg.TextItem("--")
        font = QFont()
        font.setPixelSize(20)
        self.status_text.setFont(font)
        self.status_text.setAnchor((1, 0))
        self.status_text.setPos(self.width() - 80, 0)
        self.status_text.setFlag(
            self.status_text.GraphicsItemFlag.ItemIgnoresTransformations
        )
        self.status_text.setParentItem(legend)

        # --------------------------------------------------------------------------------
        # The current block remainder,
        # it is on the center of the graph
        self.current_block_remainder_text = pg.TextItem("CBRT")
        font = QFont()
        font.setPixelSize(40)
        self.current_block_remainder_text.setFont(font)
        self.current_block_remainder_text.setAnchor((0, 0))
        self.current_block_remainder_text.setColor("red")
        self.current_block_remainder_text.setPos(
            self.width() / 2, self.height() / 2)
        self.current_block_remainder_text.setFlag(
            self.status_text.GraphicsItemFlag.ItemIgnoresTransformations
        )
        self.current_block_remainder_text.setParentItem(legend)

        # --------------------------------------------------------------------------------
        # Order the z-value of the components
        # vb.setZValue(-100)
        self.animation_img.setZValue(-100)
        legend.setZValue(-10)
        self.curve3.setZValue(1)
        self.curve1.setZValue(2)
        self.curve2.setZValue(3)

        LOGGER.debug(
            f"Initialized drawing of {self.curve1} ({self.pen1}), {self.curve2} ({self.pen2})."
        )

    def on_resized(self):
        """
        Performs actions when the widget is resized.

        Args:
            self: The instance of the widget.

        Returns:
            None
        """

        self.block_text.setAnchor((0, 0))
        self.status_text.setPos(self.width() - 80, 0)
        self.current_block_remainder_text.setPos(
            self.width() / 2, self.height() / 2)

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

    def update_animation_img(self, width: int, height: int):
        pass


class BlockManager(object):
    """
    The block manager
    @parse_blocks(blocks) is the built-in method to startup from the input blocks;
    @consume(t) is the method determine the current block and pop it if it is exceeded.
    """

    design = []

    def __init__(self, blocks=[]):
        self.design = self.parse_blocks(blocks)
        LOGGER.debug(f"Initialized {self.__class__}")

    def parse_blocks(self, blocks: list):
        """Parse the input block design

        Args:
            blocks (list): The list of blocks.

        Returns:
            list: rich information blocks.
        """
        design = []

        if len(blocks) == 0:
            LOGGER.debug("Parsed empty blocks.")
            return design

        design.append(
            dict(
                idx=0,
                name=blocks[0][0],
                duration=blocks[0][1],
                start=0,
                stop=blocks[0][1],
            )
        )
        stop = blocks[0][1]
        idx = 0

        for block in blocks[1:]:
            idx = len(design)
            duration = block[1]
            start = design[-1]["stop"]
            stop = start + duration

            design.append(
                dict(idx=idx, name=block[0],
                     duration=duration, start=start, stop=stop)
            )

        for d in design:
            d["total"] = stop
            d["blocks"] = idx + 1

        LOGGER.debug(f"Parsed blocks design: {design}")

        return design

    def consume(self, t: float):
        """
        Consumes the first block in the design list if the given time (`t`) is greater than the stop time of the block.
        Returns the consumed block or a message indicating if there are no blocks or if all blocks have been consumed.

        This method consumes a block from the `design` list based on the given time.
        If the `design` list is empty, it returns 'No block at all.'
        If the provided time is greater than the stop time of the first block in the `design` list, that block is removed from the list and a debug message is logged.
        If the `design` list becomes empty after consuming a block, it returns 'Consumed all the blocks.'
        Otherwise, it returns the first block in the `design` list.

        ** Consumed all the blocks ** is a very special output,
        it refers the blocks end, and it is a once for all output, never repeated.

        Args:
            self: The object instance.
            t (float): The time used to determine which block to consume.

        Returns:
            str or dict: The consumed block or a message indicating the status of the blocks.

        Example:
            ```python
            obj = ClassName()
            result = obj.consume(0.5)
            ```
        """

        if len(self.design) == 0:
            return "No block at all."

        if t > self.design[0]["stop"]:
            d = self.design.pop(0)
            LOGGER.debug(f"Consumed block {d}")

        if len(self.design) == 0:
            return "Consumed all the blocks."

        return self.design[0]


class UserInterfaceWidget(QtWidgets.QMainWindow):
    """My QT-6 Widget

    It is an automatically QT application.

    @update_chart(y) (method): Update the chart using the new value,
                               it append the new point to the right-most point,
                               and it pop out the first point in the left-most end.

    @_add_series() (private method): Add a series to the chart.

    """

    window_length_seconds = CONF["display"]["window_length_seconds"]
    delay_seconds = CONF["display"]["delay_seconds"]

    ref_value = CONF["display"]["ref_value"]
    max_value = CONF["display"]["max_value"]
    min_value = CONF["display"]["min_value"]
    display_ref_flag = CONF["display"]["display_ref_flag"]

    remainder_dict = CONF["experiment"]["remainder"]

    display_mode = "Realtime"
    display_modes = ["Realtime", "Delayed", "Circle fit", "Animation fit"]

    window_title = "Pressure feedback system by Dr. Zhang"

    device_reader = None
    timer = None
    block_manager = BlockManager()
    fake_blocks = []
    my_protocol = MyProtocol()
    data_folder_path = root_path.joinpath("Data")

    next_10s_step = 3
    next_10s = next_10s_step

    animation_feedback_type = "Avg."
    animation_feedback_types = ["Avg.", "Std."]
    animation_feedback_threshold = 10

    def __init__(self, app, translator=None):
        # super(MyWidget, self).__init__()
        super().__init__()

        self.app = app

        # --------------------------------------------------------------------------------
        # Start button, start the block design
        self.start_button = QtWidgets.QPushButton(tr("Start"))
        self.start_button.clicked.connect(self.start_block_design)

        # --------------------------------------------------------------------------------
        # Terminate button, terminate the on-going block design
        self.terminate_button = QtWidgets.QPushButton(tr("Terminate"))
        self.terminate_button.clicked.connect(self.terminate)
        self.terminate_button.setDisabled(True)

        # --------------------------------------------------------------------------------
        # Toggle others button, toggle the displays other than the signal monitor
        self.toggle_others_button = QtWidgets.QPushButton(tr("Toggle others"))
        self.toggle_others_button.clicked.connect(self.toggle_others)

        # --------------------------------------------------------------------------------
        # Toggle full screen display
        self.toggle_full_screen_display_button = QtWidgets.QPushButton(
            tr('Toggle full screen'))
        self.toggle_full_screen_display_button.clicked.connect(
            self.toggle_full_screen_display)

        # --------------------------------------------------------------------------------
        self.signal_monitor_widget = SignalMonitorWidget()

        # --------------------------------------------------------------------------------
        self.widget_0 = QtWidgets.QWidget()
        self.setCentralWidget(self.widget_0)

        self.widget_0_0_signal_monitor = QtWidgets.QWidget()
        self.widget_0_1_subject_stuff = QtWidgets.QWidget()
        self.widget_0_2_experiment_stuff = QtWidgets.QWidget()
        self.widget_0_3_display_stuff = QtWidgets.QWidget()

        # --------------------------------------------------------------------------------
        # Make layout 0
        layout = QtWidgets.QHBoxLayout(self.widget_0)
        layout.addWidget(self.widget_0_1_subject_stuff)
        layout.addWidget(self.widget_0_2_experiment_stuff)
        layout.addWidget(self.widget_0_3_display_stuff)
        layout.addWidget(self.widget_0_0_signal_monitor)

        # Make layout 0 0
        layout = QtWidgets.QVBoxLayout(self.widget_0_0_signal_monitor)
        widget = QtWidgets.QWidget()
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)
        hbox.addWidget(self.start_button)
        hbox.addWidget(self.terminate_button)
        hbox.addWidget(self.toggle_full_screen_display_button)
        hbox.addWidget(self.toggle_others_button)
        layout.addWidget(widget)
        layout.addWidget(self.signal_monitor_widget)

        # Make layout 0 1
        layout = QtWidgets.QVBoxLayout(self.widget_0_1_subject_stuff)
        self.subject_inputs = self.subject_stuff(layout)

        # Make layout 0 2
        layout = QtWidgets.QVBoxLayout(self.widget_0_2_experiment_stuff)
        self.experiment_inputs = self.experiment_stuff(layout)

        # Make layout 0 3
        layout = QtWidgets.QVBoxLayout(self.widget_0_3_display_stuff)
        self.display_inputs = self.display_stuff(layout)

        # # Handle resize event
        # self.resizeEvent.connect(self.on_resized)

    def keyPressEvent(self, event):
        # F11 key code is 16777274
        known_key_code = {
            16777274: 'F11'
        }

        if known_key_code.get(event.key()) == 'F11':
            self.toggle_full_screen_display()

    def toggle_full_screen_display(self):
        if QtCore.Qt.WindowFullScreen & self.windowState():
            # is showFullScreen
            self.showNormal()
            LOGGER.debug('Entered show normal state')
        else:
            # is not showFullScreen
            self.showFullScreen()
            LOGGER.debug('Entered show full screen state')

    def toggle_others(self):
        # self.layout03.hide()
        for e in [self.widget_0_1_subject_stuff, self.widget_0_2_experiment_stuff, self.widget_0_3_display_stuff]:
            e.setHidden(not e.isHidden())
            LOGGER.debug(f'Set display of {e} to hidden: {e.isHidden()}')

    def resizeEvent(self, event):
        """
        Handles the resize event of the main window.

        Args:
            self: The instance of the main window.
            event: The resize event object.

        Returns:
            None
        """

        self.signal_monitor_widget.on_resized()

        LOGGER.debug(f"Main window resized to size {event}")

    def restart_reader(self, reader: RealTimeHidReader):
        """
        Link to the hid device reader.

        Args:
            reader (RealTimeHidReader): _description_
        """

        if self.device_reader is not None:
            pairs = self.device_reader.stop()
            time.sleep(0.1)
            LOGGER.warning(
                f"Closed existing device reader, discharging {len(pairs)} pnts data"
            )

        # Reset the next_10s timer
        self.next_10s = self.next_10s_step

        reader.delay_seconds = self.delay_seconds

        self.device_reader = reader

        reader.start()

        LOGGER.debug(f"Linked with device reader: {reader}")

        self.setWindowTitle(tr(self.window_title))

        if self.timer is not None:
            self.timer.stop()
            LOGGER.warning(f"Stopped existing timer {self.timer}")

        def update():
            pairs = reader.peek_by_seconds(self.window_length_seconds)
            pairs_delay = reader.peek_by_seconds(
                self.window_length_seconds, peek_delay=True
            )

            # not received any valid data,
            # something is wrong.
            if len(pairs) == 0:
                # LOGGER.error(f'Failed receive valid data')
                return

            self.update_graph(pairs, pairs_delay)

        timer = QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start()

        # Handle the timer, so I can stop it.
        self.timer = timer

    @QtCore.Slot()
    def terminate(self):
        """Terminate the current block design experiment."""
        self.block_manager = BlockManager()

        self.fake_blocks = [
            e for e in self.block_manager.design if e["name"] == "Fake"]
        LOGGER.debug(f"Found fake blocks {self.fake_blocks}")

        self.start_button.setDisabled(False)
        self.terminate_button.setDisabled(True)
        LOGGER.debug(
            "Terminated block designed experiment, and the start_button disable status is released."
        )

    @QtCore.Slot()
    def start_block_design(self):
        """
        Start the block design experiment form the current setup.

        It also restarts the self.device_reader.
        """

        # Reset score animation
        sa.reset()

        self.start_button.setDisabled(True)
        self.terminate_button.setDisabled(False)

        self.block_manager = BlockManager(self.experiment_inputs["_buffer"])

        self.fake_blocks = [
            e for e in self.block_manager.design if e["name"] == "Fake"]
        LOGGER.debug(f"Found fake blocks {self.fake_blocks}")

        if len(self.block_manager.design) == 0:
            self.start_button.setDisabled(False)
            self.terminate_button.setDisabled(True)
            LOGGER.warning(
                "Tried to start the block designed experiment, but no design was found."
            )
            return

        # Snapshot the current setup.
        self.setup_snapshot = dict(
            subject_info=self.subject_inputs["_summary"].toPlainText(),
            experiment_info=self.experiment_inputs["_buffer"],
        )

        self.device_reader.stop()
        time.sleep(0.1)
        self.device_reader.start()

        # Reset the next_10s timer
        self.next_10s = self.next_10s_step

    def save_data(self):
        """
        Save the data and the snapshot setup for the block design experiment.

        It also restarts the self.device_reader.
        """
        data = self.device_reader.stop()

        subject_info = self.setup_snapshot["subject_info"]
        experiment_info = self.setup_snapshot["experiment_info"]

        _filename = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")
        folder = self.data_folder_path.joinpath(f'{_filename}')

        folder.mkdir(exist_ok=True, parents=True)

        json.dump(data, open(folder.joinpath("data.json"), "w"))
        json.dump(subject_info, open(folder.joinpath("subject.json"), "w"))
        json.dump(experiment_info, open(
            folder.joinpath("experiment.json"), "w"))

        LOGGER.debug(f"Saved data into {folder}")

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
            return tr(s, "display setup session")

        inputs = dict(
            # Select display mode
            display_mode=QtWidgets.QComboBox(),
            # Real time curve
            line1_color=QtWidgets.QPushButton("    "),
            line1_width=QtWidgets.QSpinBox(),
            grid_toggle=QtWidgets.QCheckBox(),
            # Delayed curve
            line2_color=QtWidgets.QPushButton("    "),
            line2_width=QtWidgets.QSpinBox(),
            line2_delay=QtWidgets.QSpinBox(),
            # Ref. curve
            zone3=QtWidgets.QGroupBox(_tr("Ref. value")),
            line3_color=QtWidgets.QPushButton("    "),
            line3_width=QtWidgets.QSpinBox(),
            line3_ref_value=QtWidgets.QDial(),
            line3_ref_value_spin=QtWidgets.QSpinBox(),
            # Animation
            animation_value_type=QtWidgets.QComboBox(),
            animation_value_threshold=QtWidgets.QDial(),
            # Correction
            button_0g=QtWidgets.QPushButton(_tr("Ruler correction 0g")),
            button_200g=QtWidgets.QPushButton(_tr("Ruler correction 200g")),
            button_offset_0g=QtWidgets.QPushButton(_tr("Zero correction 0g"))
        )

        def pen2hex(pen):
            rgb = list(pen.color().toTuple())[:3]
            string = "#" + "".join([hex(e).replace("x", "")[-2:] for e in rgb])
            return string

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox(_tr("Display setup"))
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        main_box_layout = QtWidgets.QVBoxLayout()
        groupbox.setLayout(main_box_layout)

        # --------------------------------------------------------------------------------
        inputs["display_mode"].addItems(self.display_modes)
        inputs["display_mode"].setCurrentText(self.display_mode)

        main_box_layout.addWidget(inputs["display_mode"])

        # --------------------------------------------------------------------------------
        zone1 = QtWidgets.QGroupBox(_tr("Curve (realtime)"))
        main_box_layout.addWidget(zone1)
        vbox1 = QtWidgets.QVBoxLayout()
        zone1.setLayout(vbox1)

        hbox = QtWidgets.QHBoxLayout()
        vbox1.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Color")))
        hbox.addWidget(inputs["line1_color"])

        hbox = QtWidgets.QHBoxLayout()
        vbox1.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Width")))
        hbox.addWidget(inputs["line1_width"])

        inputs["line1_width"].setValue(2)
        inputs["line1_width"].setMinimum(1)
        inputs["line1_width"].setMaximum(10)

        hbox = QtWidgets.QHBoxLayout()
        vbox1.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Grid Toggle")))
        hbox.addWidget(inputs['grid_toggle'])

        # --------------------------------------------------------------------------------
        zone2 = QtWidgets.QGroupBox(_tr("Curve (delay)"))
        main_box_layout.addWidget(zone2)
        vbox2 = QtWidgets.QVBoxLayout()
        zone2.setLayout(vbox2)

        hbox = QtWidgets.QHBoxLayout()
        vbox2.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Delay (seconds)")))
        hbox.addWidget(inputs["line2_delay"])

        hbox = QtWidgets.QHBoxLayout()
        vbox2.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Color")))
        hbox.addWidget(inputs["line2_color"])

        hbox = QtWidgets.QHBoxLayout()
        vbox2.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Width")))
        hbox.addWidget(inputs["line2_width"])

        inputs["line2_width"].setValue(2)
        inputs["line2_width"].setMinimum(1)
        inputs["line2_width"].setMaximum(10)

        # --------------------------------------------------------------------------------
        inputs["line2_delay"].setValue(10)
        inputs["line2_delay"].setMinimum(1)
        inputs["line2_delay"].setMaximum(10)

        def _change_delay(delay):
            self.delay_seconds = delay
            self.device_reader.recompute_delay(delay)
            self.restart_reader(self.device_reader)

        inputs["line2_delay"].valueChanged.connect(_change_delay)

        # --------------------------------------------------------------------------------
        zone_animation = QtWidgets.QGroupBox(_tr("Animation opt."))
        zone_animation.setCheckable(True)
        main_box_layout.addWidget(zone_animation)
        vbox_animation = QtWidgets.QVBoxLayout()
        zone_animation.setLayout(vbox_animation)

        animation_value_type = inputs["animation_value_type"]
        animation_value_type.addItems(self.animation_feedback_types)
        vbox_animation.addWidget(QtWidgets.QLabel(_tr("Feedback")))
        vbox_animation.addWidget(animation_value_type)

        def _change_feedback_type(idx):
            value = self.animation_feedback_types[idx]
            self.animation_feedback_type = value
            LOGGER.debug(f"Changed animation feedback type into: {value}")

        animation_value_type.currentIndexChanged.connect(_change_feedback_type)

        hbox = QtWidgets.QHBoxLayout()
        vbox_animation.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Threshold")))
        label_threshold = QtWidgets.QLabel()
        hbox.addWidget(label_threshold)
        vbox_animation.addWidget(inputs["animation_value_threshold"])

        def _label_threshold_changed(value):
            label_threshold.setText(f"{value}")
            self.animation_feedback_threshold = value
            LOGGER.debug(f"Changed animation feedback threshold into: {value}")

        inputs["animation_value_threshold"].valueChanged.connect(
            _label_threshold_changed
        )

        inputs["animation_value_threshold"].setValue(10)
        inputs["animation_value_threshold"].setMinimum(1)
        inputs["animation_value_threshold"].setMaximum(200)

        # --------------------------------------------------------------------------------
        zone3 = inputs["zone3"]
        zone3.setCheckable(True)
        main_box_layout.addWidget(zone3)
        vbox3 = QtWidgets.QVBoxLayout()
        zone3.setLayout(vbox3)

        hbox = QtWidgets.QHBoxLayout()
        vbox3.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Color")))
        hbox.addWidget(inputs["line3_color"])

        hbox = QtWidgets.QHBoxLayout()
        vbox3.addLayout(hbox)
        hbox.addWidget(QtWidgets.QLabel(_tr("Width")))
        hbox.addWidget(inputs["line3_width"])

        hbox = QtWidgets.QHBoxLayout()
        vbox3.addLayout(hbox)

        # --------------------
        # Ref. line
        hbox.addWidget(QtWidgets.QLabel(_tr("Ref. value")))
        label = QtWidgets.QLabel("500")
        hbox.addWidget(label)
        vbox3.addWidget(inputs["line3_ref_value_spin"])
        vbox3.addWidget(inputs["line3_ref_value"])

        inputs["line3_width"].setMinimum(1)
        inputs["line3_width"].setMaximum(10)
        inputs["line3_width"].setValue(2)

        inputs["line3_ref_value"].setMinimum(1)
        inputs["line3_ref_value"].setMaximum(2000)
        inputs["line3_ref_value"].setValue(500)

        inputs["line3_ref_value_spin"].setMinimum(1)
        inputs["line3_ref_value_spin"].setMaximum(2000)
        inputs["line3_ref_value_spin"].setValue(500)

        # --------------------
        # Link line3_ref_value and line3_ref_value_spin
        def _change_ref_value(v):
            self.ref_value = v
            inputs['line3_ref_value_spin'].setValue(v)
            self.signal_monitor_widget.ellipse4_size_changed(v)
            label.setText("{}".format(v))

        def _change_ref_value_spin(v):
            self.ref_value = v
            inputs['line3_ref_value'].setValue(v)
            self.signal_monitor_widget.ellipse4_size_changed(v)
            label.setText("{}".format(v))

        inputs["line3_ref_value"].valueChanged.connect(_change_ref_value)
        inputs["line3_ref_value_spin"].valueChanged.connect(
            _change_ref_value_spin)

        def _check_zone3(b):
            self.display_ref_flag = b

        zone3.toggled.connect(_check_zone3)

        # --------------------------------------------------------------------------------
        zone4 = QtWidgets.QGroupBox(_tr("Correction"))
        zone4.setCheckable(True)
        zone4.setChecked(False)
        main_box_layout.addWidget(zone4)
        vbox4 = QtWidgets.QVBoxLayout()
        zone4.setLayout(vbox4)

        vbox4.addWidget(inputs["button_0g"])
        vbox4.addWidget(inputs["button_200g"])
        vbox4.addWidget(inputs["button_offset_0g"])

        def _write_to_correction(name, num):
            p = root_path.joinpath(f"correction/{name}")
            with open(p, "w") as f:
                f.write(f"{num}")
            LOGGER.debug(f"Wrote correction {name}({num}) to {p}")

        def _correction_0g():
            pairs = self.device_reader.peek(100)
            n = len(pairs)
            if n == 0:
                LOGGER.warning(
                    "Failed to correct with the 0 g, since the data is empty")
                return
            g0 = int(sum(e[1] for e in pairs) / n)
            self.device_reader.g0 = g0
            self.device_reader.offset_g0 = g0
            threading.Thread(
                target=_write_to_correction,
                args=('g0', g0)).start()
            threading.Thread(
                target=_write_to_correction,
                args=('offset_g0', g0)).start()
            LOGGER.debug(f"Re-correct the g0 to {g0} (with {n} points)")
            LOGGER.debug(f"Re-correct the offset_g0 to {g0} (with {n} points)")

        def _correction_200g():
            pairs = self.device_reader.peek(100)
            n = len(pairs)
            if n == 0:
                LOGGER.warning(
                    "Failed to correct with the 200 g, since the data is empty"
                )
                return
            g200 = int(sum(e[1] for e in pairs) / n)
            self.device_reader.g200 = g200
            threading.Thread(
                target=_write_to_correction,
                args=('g200', g200)).start()
            LOGGER.debug(f"Re-correct the g200 to {g200} (with {n} points)")

        def _correction_offset_0g():
            pairs = self.device_reader.peek(100)
            n = len(pairs)
            if n == 0:
                LOGGER.warning(
                    "Failed to correct with the offset 0 g, since the data is empty"
                )
                return
            offset_g0 = int(sum(e[1] for e in pairs) / n)
            self.device_reader.offset_g0 = offset_g0
            threading.Thread(
                target=_write_to_correction,
                args=('offset_g0', offset_g0)).start()
            LOGGER.debug(
                f"Re-correct the offset_g0 to {offset_g0} (with {n} points)")

        inputs["button_0g"].clicked.connect(_correction_0g)
        inputs["button_200g"].clicked.connect(_correction_200g)
        inputs["button_offset_0g"].clicked.connect(_correction_offset_0g)

        # --------------------------------------------------------------------------------

        def _fit_color1():
            inputs["line1_color"].setStyleSheet(
                "QPushButton {background-color: "
                + pen2hex(self.signal_monitor_widget.pen1)
                + "}"
            )

        def _change_color1():
            qColor = QtWidgets.QColorDialog(self).getColor(
                self.signal_monitor_widget.pen1.color()
            )

            if not qColor.isValid():
                return

            self.signal_monitor_widget.pen1.setColor(qColor)
            _fit_color1()

            LOGGER.debug(f"Set line1 color to: {qColor}")

        def _change_width1(width):
            self.signal_monitor_widget.pen1.setWidth(width)

        _fit_color1()
        _change_width1(2)

        inputs["line1_color"].clicked.connect(_change_color1)
        inputs["line1_width"].valueChanged.connect(_change_width1)

        # --------------------------------------------------------------------------------
        def _fit_color2():
            inputs["line2_color"].setStyleSheet(
                "QPushButton {background-color: "
                + pen2hex(self.signal_monitor_widget.pen2)
                + "}"
            )

        def _change_color2():
            qColor = QtWidgets.QColorDialog(self).getColor(
                self.signal_monitor_widget.pen2.color()
            )

            if not qColor.isValid():
                return

            self.signal_monitor_widget.pen2.setColor(qColor)
            _fit_color2()

            LOGGER.debug(f"Set line2 color to: {qColor}")

        def _change_width2(width):
            self.signal_monitor_widget.pen2.setWidth(width)

        _fit_color2()
        _change_width2(2)

        inputs["line2_color"].clicked.connect(_change_color2)
        inputs["line2_width"].valueChanged.connect(_change_width2)

        # --------------------------------------------------------------------------------
        def _fit_color3():
            inputs["line3_color"].setStyleSheet(
                "QPushButton {background-color: "
                + pen2hex(self.signal_monitor_widget.pen3)
                + "}"
            )

        def _change_color3():
            qColor = QtWidgets.QColorDialog(self).getColor(
                self.signal_monitor_widget.pen3.color()
            )

            if not qColor.isValid():
                return

            self.signal_monitor_widget.pen3.setColor(qColor)
            _fit_color3()

            LOGGER.debug(f"Set line3 color to: {qColor}")

        def _change_width3(width):
            self.signal_monitor_widget.pen3.setWidth(width)

        _fit_color3()
        _change_width3(2)

        inputs["line3_color"].clicked.connect(_change_color3)
        inputs["line3_width"].valueChanged.connect(_change_width3)

        # --------------------------------------------------------------------------------
        def _change_display_mode(mode):
            self.display_mode = mode

            # zone1: option for realtime curve
            # zone2: option for delayed curve
            # zone3: option for reference pressure value
            # zone4: weight correction

            if mode == "Realtime":
                zone1.setVisible(True)
                zone2.setVisible(False)
                zone3.setVisible(True)
                zone4.setVisible(True)
                zone_animation.setVisible(False)

            if mode == "Delayed":
                zone1.setVisible(True)
                zone2.setVisible(True)
                zone3.setVisible(True)
                zone4.setVisible(True)
                zone_animation.setVisible(False)

            if mode == "Animation fit":
                zone1.setVisible(False)
                zone2.setVisible(True)
                zone3.setVisible(True)
                zone4.setVisible(False)
                zone_animation.setVisible(True)

        inputs["display_mode"].currentTextChanged.connect(_change_display_mode)
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
            return tr(s, "experiment setup session")

        inputs = dict(
            predefined=QtWidgets.QComboBox(),
            seconds=QtWidgets.QSpinBox(),
            # --------------------
            real=QtWidgets.QPushButton(_tr("Real")),
            fake=QtWidgets.QPushButton(_tr("Fake")),
            hide=QtWidgets.QPushButton(_tr("Hide")),
            # --------------------
            repeat=QtWidgets.QPushButton(_tr("Repeat")),
            clear=QtWidgets.QPushButton(_tr("Clear")),
            # --------------------
            save=QtWidgets.QPushButton(_tr("Save")),
            load_fake=QtWidgets.QPushButton(_tr("Load fake")),
            # --------------------
            fake_file_info=QtWidgets.QLabel("N.A."),
            # --------------------
            # _summary=QtWidgets.QTextEdit(),
            _summary=QtWidgets.QTextBrowser(),
            _buffer=[],
        )

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox(_tr("Experiment setup"))
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Predefined protocols")))
        vbox.addWidget(inputs["predefined"])

        for k, v in self.my_protocol.protocols.items():
            txt = f'{k} | {v.get("name", "")}'
            inputs["predefined"].addItems([txt])

        def _change_protocol():
            protocol = inputs["predefined"].currentText()
            k = protocol.split(" | ")[0]
            _clear()
            inputs["_buffer"] = self.my_protocol.get_buffer(k)
            _update_summary()

        inputs["predefined"].currentTextChanged.connect(_change_protocol)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Block length (seconds)")))
        vbox.addWidget(inputs["seconds"])
        inputs["seconds"].setValue(10)
        inputs["seconds"].setMaximum(3600)
        inputs["seconds"].setMinimum(1)

        # --------------------------------------------------------------------------------
        widget = QtWidgets.QWidget()
        vbox.addWidget(widget)
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)
        hbox.addWidget(inputs["real"])
        hbox.addWidget(inputs["fake"])
        hbox.addWidget(inputs['hide'])

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Summary")))
        vbox.addWidget(inputs["_summary"])

        # --------------------------------------------------------------------------------
        # The hbox inside the current vbox layout
        # It contains 3 buttons
        widget = QtWidgets.QWidget()
        vbox.addWidget(widget)
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)

        hbox.addWidget(inputs["repeat"])
        hbox.addWidget(inputs["clear"])

        # --------------------------------------------------------------------------------
        # The single button inside the current vbox layout
        # It contains the save experiment design button
        vbox.addWidget(inputs["save"])

        def _save():
            name, ok = QtWidgets.QInputDialog.getText(
                self, "Save protocol", "Description:"
            )

            if ok:
                print(f"Saving {name}")
                self.my_protocol.save(name, inputs["_buffer"])

        inputs["save"].clicked.connect(_save)

        # --------------------------------------------------------------------------------
        # The hbox inside the current vbox layout
        # It contains load fake pressure file and its info label
        widget = QtWidgets.QWidget()
        vbox.addWidget(widget)
        hbox = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox)

        hbox.addWidget(inputs["load_fake"])
        hbox.addWidget(inputs["fake_file_info"])

        def _load_fake():
            output = QtWidgets.QFileDialog.getExistingDirectory(
                self,
                _tr("Select fake pressure data folder"),
                self.data_folder_path.as_posix(),
            )

            if output is None or output == "":
                LOGGER.warning(
                    "Not selected any directory for loading fake pressure data."
                )
                return

            folder = Path(output)
            data_file = folder.joinpath("data.json")

            if not folder.is_dir():
                LOGGER.error(
                    f"Invalid directory for loading fake pressure: {folder}")
                return

            if not data_file.is_file():
                LOGGER.error(
                    f"Invalid data file for loading fake pressure: {data_file}"
                )
                return

            n, stats = self.device_reader.fake_pressure.load_file(data_file)

            inputs["fake_file_info"].setText(
                f"{data_file.relative_to(self.data_folder_path)}\n{stats}"
            )

            LOGGER.debug(
                f"Loaded fake pressure data ({n} points): {data_file}")

            return

        inputs["load_fake"].clicked.connect(_load_fake)

        # --------------------------------------------------------------------------------

        def _update_summary():
            n = 0
            length = 0
            text = []
            for type, value in inputs["_buffer"]:
                n += 1
                length += value
                text.append(f"{n:03d}: {type}\t: {value}\t: {length}")

            text = [
                "# Automatic generated task design",
                f"# Blocks: {n}",
                f"# Costs: {length} seconds",
                "",
                "# Real: Block with real feedback",
                "# Fake: Block with fake feedback",
                "# Hide: Block with empty screen",
                "",
                "Idx: Type\t: Block\t: Total",
            ] + text

            return inputs["_summary"].setText("\n".join(text))

        def _clear():
            inputs["_buffer"] = []
            _update_summary()

        def _repeat():
            inputs["_buffer"] += inputs["_buffer"]
            _update_summary()

        def _add_block(block):
            seconds = int(inputs["seconds"].text())
            inputs["_buffer"].append((block, seconds))
            _update_summary()

        def _add_block_real():
            _add_block("Real")

        def _add_block_fake():
            _add_block("Fake")

        def _add_block_hide():
            _add_block("Hide")

        inputs["clear"].clicked.connect(_clear)
        inputs["repeat"].clicked.connect(_repeat)

        inputs["real"].clicked.connect(_add_block_real)
        inputs["fake"].clicked.connect(_add_block_fake)
        inputs["hide"].clicked.connect(_add_block_hide)

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
            return tr(s, "subject setup session")

        inputs = dict(
            date=QtWidgets.QDateTimeEdit(),
            subject=QtWidgets.QLineEdit(),
            gender=QtWidgets.QComboBox(),
            # age=QtWidgets.QDial(),
            age=QtWidgets.QSpinBox(),
            _summary=QtWidgets.QTextEdit(),
        )

        def _tr(s):
            return tr(s, "subject setup session")

        # --------------------------------------------------------------------------------
        groupbox = QtWidgets.QGroupBox(_tr("Subject setup"))
        groupbox.setCheckable(True)
        layout.addWidget(groupbox)
        vbox = QtWidgets.QVBoxLayout()
        groupbox.setLayout(vbox)

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Experiment date")))
        vbox.addWidget(inputs["date"])
        inputs["date"].setDateTime(QtCore.QDateTime.currentDateTime())

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Subject name")))
        vbox.addWidget(inputs["subject"])
        inputs["subject"].setPlaceholderText(_tr("Subject name"))

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Subject gender")))
        inputs["gender"].addItems([_tr("male"), _tr("female")])
        vbox.addWidget(inputs["gender"])

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Subject age")))
        inputs["age"].setRange(1, 40)
        inputs["age"].setSingleStep(1)
        inputs["age"].setValue(7)
        vbox.addWidget(inputs["age"])

        # --------------------------------------------------------------------------------
        vbox.addWidget(QtWidgets.QLabel(_tr("Summary")))
        vbox.addWidget(inputs["_summary"])

        # --------------------------------------------------------------------------------
        def onchange():
            text = "\n".join(
                [
                    f"Date: {inputs['date'].dateTime().toString()}",
                    f"Subject: {inputs['subject'].text()}",
                    f"Gender: {inputs['gender'].currentText()}",
                    f"Age: {inputs['age'].value()}",
                ]
            )
            inputs["_summary"].setText(text)

        inputs["date"].dateTimeChanged.connect(onchange)
        inputs["subject"].textChanged.connect(onchange)
        inputs["gender"].currentTextChanged.connect(onchange)
        inputs["age"].valueChanged.connect(onchange)

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

        if not pairs:
            return

        t0 = pairs[0][-1]
        t1 = pairs[-1][-1]

        # Compute the sampling rate in real time,
        # and update the status_text component accordingly.
        n = len(pairs) - 1
        sample_rate = n / max(t1 - t0, 1e-4)
        self.signal_monitor_widget.status_text.setText(f"{sample_rate:.2f} Hz")

        block = self.block_manager.consume(t1)

        if block == "Consumed all the blocks.":
            self.signal_monitor_widget.block_text.setText("Finished")
            LOGGER.debug("Block design is completed.")
            self.fake_blocks = []
            self.save_data()
            return

        if block == "No block at all.":
            self.signal_monitor_widget.block_text.setText(
                f"Idle {pairs[-1][0]:.2f}")
            self.signal_monitor_widget.current_block_remainder_text.setText(
                self.remainder_dict.get("NA", "--")
            )
            return t0, t1, ""

        # Compute the block status in real time,
        # and update the block_text component accordingly.
        if isinstance(block, dict):
            block_name = block["name"]
            block_start = block["start"]
            stop = block["stop"]
            total = block["total"]
            duration = block["duration"]

            txt = f"{block_name} | {stop-t1:.0f} | {total-t1:.0f}"

            self.signal_monitor_widget.block_text.setText(txt)
            self.signal_monitor_widget.current_block_remainder_text.setText(
                self.remainder_dict.get(block_name, "--")
            )

        return t0, t1, block_name

    def update_curve13(
        self, pairs: list, t0: float, t1: float, block_name: str, expand_t: float = 0
    ):
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
            t0, max(t1, self.window_length_seconds) + expand_t, padding=0
        )

        if block_name == "Hide":
            # Hide the feedback curves if the block_name is "hide"
            self.signal_monitor_widget.update_curve1([])
            self.signal_monitor_widget.update_curve3(0, 0, 0, False)
        else:
            # Otherwise, show the curves
            self.signal_monitor_widget.update_curve1(pairs)
            self.signal_monitor_widget.update_curve3(
                t0,
                max(t1, self.window_length_seconds) + expand_t,
                self.ref_value,
                self.display_ref_flag,
            )

    def update_curve2(self, pairs_delay: list):
        """
        Update the curve2 (the delayed curve)

        Args:
            pairs_delay (list): The delayed mean value of the incoming new data.
        """
        if pairs_delay is None:
            return

        self.signal_monitor_widget.update_curve2(pairs_delay)

    def _resize_animation_img(self):
        w = self.signal_monitor_widget.animation_img.width()
        pw = self.signal_monitor_widget.animation_img.pixelWidth()
        h = self.signal_monitor_widget.animation_img.height()
        ph = self.signal_monitor_widget.animation_img.pixelHeight()

        sa.width = int(w / pw)
        sa.height = int(h / ph)

        # print(w, pw, h, ph)

    def _compare_animation_feedback(self, values):
        avg, std, _ = values

        step = 0

        if self.animation_feedback_type == "Std.":
            if std > self.animation_feedback_threshold:
                step = -10
            if std <= self.animation_feedback_threshold:
                step = 10

            LOGGER.debug(
                f"Compare animation feedback (std), {step}, {std}, {self.animation_feedback_threshold}"
            )

        if self.animation_feedback_type == "Avg.":
            diff = np.abs(avg - self.ref_value)
            if diff > self.animation_feedback_threshold:
                step = -10
            if diff <= self.animation_feedback_threshold:
                step = 10
            LOGGER.debug(
                f"Compare animation feedback (avg), {step}, {diff}, {self.animation_feedback_threshold}"
            )

        score = sa.safe_update_score(step)

        LOGGER.debug(f"Update score to: {score}, step: {step}")

        return score

    def update_animation_img(self, flag_10s: bool, pairs=None):
        # Enter into the animation mode
        self.signal_monitor_widget.animation_mode()

        if flag_10s:
            self._resize_animation_img()

            if pairs:
                score = self._compare_animation_feedback(pairs[-1])
            else:
                score = sa.score

            # Random assign score
            # score = np.random.randint(1, 99)

            # sa.mk_frames(score)
            Thread(target=sa.mk_frames, args=(score,), daemon=True).start()

        # Draw the tiny window for pressure feedback
        mat = pil2rgb(sa.tiny_window(sa.img, ref=self.ref_value, pairs=pairs))
        self.signal_monitor_widget.animation_img.setImage(
            mat[::-1].transpose([1, 0, 2])
        )

    def _setup_display_modes_inside_monitor(self):
        """
        Setup visible value for the curves according to the current self.display_mode
        """
        if self.display_mode == "Delayed":
            self.signal_monitor_widget.curve1.setVisible(True)
            self.signal_monitor_widget.curve2.setVisible(True)
            self.signal_monitor_widget.curve3.setVisible(
                self.display_inputs["zone3"].isChecked()
            )
            self.signal_monitor_widget.ellipse4.setVisible(False)
            self.signal_monitor_widget.ellipse5.setVisible(False)
            self.signal_monitor_widget.animation_img.setVisible(False)
            self.signal_monitor_widget.current_block_remainder_text.setVisible(
                True)

        if self.display_mode == "Realtime":
            self.signal_monitor_widget.curve1.setVisible(True)
            self.signal_monitor_widget.curve2.setVisible(False)
            self.signal_monitor_widget.curve3.setVisible(
                self.display_inputs["zone3"].isChecked()
            )
            self.signal_monitor_widget.ellipse4.setVisible(False)
            self.signal_monitor_widget.ellipse5.setVisible(False)
            self.signal_monitor_widget.animation_img.setVisible(False)
            self.signal_monitor_widget.current_block_remainder_text.setVisible(
                True)

        if self.display_mode == "Circle fit":
            self.signal_monitor_widget.curve1.setVisible(False)
            self.signal_monitor_widget.curve2.setVisible(False)
            self.signal_monitor_widget.curve3.setVisible(False)
            self.signal_monitor_widget.ellipse4.setVisible(True)
            self.signal_monitor_widget.ellipse5.setVisible(True)
            self.signal_monitor_widget.animation_img.setVisible(False)
            self.signal_monitor_widget.current_block_remainder_text.setVisible(
                True)

        if self.display_mode == "Animation fit":
            self.signal_monitor_widget.curve1.setVisible(False)
            self.signal_monitor_widget.curve2.setVisible(False)
            self.signal_monitor_widget.curve3.setVisible(False)
            self.signal_monitor_widget.ellipse4.setVisible(False)
            self.signal_monitor_widget.ellipse5.setVisible(False)
            self.signal_monitor_widget.animation_img.setVisible(True)
            self.signal_monitor_widget.current_block_remainder_text.setVisible(
                False)

    def update_graph(self, pairs: list, pairs_delay: list):
        """
        Update the graph as the very fast loop

        Args:
            pairs (list): The incoming data from the hid device. Defaults to None.
        """
        current_block = self.update_signal_experiment_status(pairs)

        # Doing nothing is current block is None
        if current_block is None:
            return

        # Automatically toggle the display status of the graph components
        self._setup_display_modes_inside_monitor()

        # The t0, t1 is the start, stop time of the incoming data
        # The block_name is one of ['Real', 'Fake', 'Empty']
        t0, t1, block_name = current_block

        # Make sure the points inside the fake blocks are correctly re-assigned
        # The re-assignment is cut off the 1st and 2nd elements of the array,
        # it makes sure the fake pressure value is on the head of the array.
        pairs = [
            p[2:]
            if any(
                p[-1] > fb["start"] and p[-1] < fb["stop"] for fb in self.fake_blocks
            )
            else p
            for p in pairs
        ]

        # The buffer_delay's row is:
        # (avg-pressure, fake-avg-pressure, std-pressure, fake-std-pressure, timestampe)
        # This uses the columns for both avg. (0|1), std. (2|3) values, and timestamp (4)
        # The output pairs_delay's row is (avg, std, timestamp)
        pairs_delay = [
            (p[1], p[3], p[4])
            if any(
                p[-1] + self.delay_seconds > fb["start"]
                and p[-1] + self.delay_seconds < fb["stop"]
                for fb in self.fake_blocks
            )
            else (p[0], p[2], p[4])
            for p in pairs_delay
        ]

        # Display the animation img
        if self.display_mode == "Animation fit":
            flag_10s = False

            while t1 > self.next_10s:
                LOGGER.debug(f"The 10s gap is reached, {self.next_10s}")
                self.next_10s += self.next_10s_step
                flag_10s = True

            self.update_animation_img(flag_10s, pairs_delay)
            return

        # Enter the curve mode for the monitor
        _ref_value = self.ref_value
        _show_grid_flag = self.display_inputs['grid_toggle'].isChecked()

        if self.display_mode == 'Circle fit':
            _ref_value = None
            _show_grid_flag = False

        # print(dir(self.display_inputs['grid_toggle']))
        self.signal_monitor_widget.enter_curve_mode(
            _ref_value, _show_grid_flag, _show_grid_flag)

        if self.display_mode == "Delayed":
            # The expand_t setup is to make sure the delayed curve is kept on the center.
            self.update_curve13(
                pairs,
                t0,
                t1,
                block_name,
                expand_t=self.window_length_seconds - self.delay_seconds * 2,
            )

            if block_name != "Empty":
                self.update_curve2(pairs_delay)

        if self.display_mode == "Realtime":
            self.update_curve13(
                pairs, t0, t1, block_name, expand_t=self.window_length_seconds
            )

        if self.display_mode == "Circle fit":
            self.signal_monitor_widget.setXRange(
                self.signal_monitor_widget.min_value,
                self.signal_monitor_widget.max_value,
            )
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
