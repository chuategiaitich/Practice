import sys
import re
import serial
import serial.tools.list_ports
import threading
from time import time
from collections import defaultdict
from PyQt6.QtCore import pyqtSignal, QObject, QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QLabel, QScrollArea, QFrame, QComboBox, QGroupBox, QMessageBox, QLineEdit,
    QGridLayout
)
import pyqtgraph as pg


class SerialReader(QObject):
    new_data = pyqtSignal(str, float)

    def __init__(self):
        super().__init__()
        self.serial = None
        self.running = False
        self.pattern = re.compile(r">(\w+):\s*(-?\d+\.?\d*)")

    def start(self, port, baudrate, parity, databits, stopbits):
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                parity=parity,
                bytesize=databits,
                stopbits=stopbits,
                timeout=1
            )
            self.running = True
            threading.Thread(target=self.read_loop, daemon=True).start()
        except Exception as e:
            QMessageBox.critical(None, "Serial Error", f"Could not open serial port:\n{e}")

    def read_loop(self):
        while self.running and self.serial and self.serial.is_open:
            try:
                line = self.serial.readline().decode("utf-8").strip()
                matches = self.pattern.findall(line)
                for label, value in matches:
                    self.new_data.emit(label, float(value))
            except Exception:
                pass

    def send(self, data):
        if self.serial and self.serial.is_open:
            self.serial.write(data.encode("utf-8") + b"\n")

    def stop(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()


class SerialPlotter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Realtime Serial Plotter")
        self.resize(1200, 600)

        main_layout = QVBoxLayout(self)
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.showGrid(x=True, y=True)
        main_layout.addWidget(self.plotWidget)

        config_toggle_layout = QHBoxLayout()
        main_layout.addLayout(config_toggle_layout)

        # Serial Config
        self.serialGroup = QGroupBox("Serial Config")
        config_layout = QVBoxLayout(self.serialGroup)
        self.portBox = QComboBox()
        self.baudBox = QComboBox()
        self.parityBox = QComboBox()
        self.databitsBox = QComboBox()
        self.stopbitsBox = QComboBox()
        self.refreshButton = QPushButton("Refresh Ports")
        self.connectButton = QPushButton("Connect")
        self.disconnectButton = QPushButton("Disconnect")

        config_layout.addWidget(QLabel("Port:"))
        config_layout.addWidget(self.portBox)
        config_layout.addWidget(self.refreshButton)
        config_layout.addWidget(QLabel("Baudrate:"))
        config_layout.addWidget(self.baudBox)
        config_layout.addWidget(QLabel("Parity:"))
        config_layout.addWidget(self.parityBox)
        config_layout.addWidget(QLabel("Data Bits:"))
        config_layout.addWidget(self.databitsBox)
        config_layout.addWidget(QLabel("Stop Bits:"))
        config_layout.addWidget(self.stopbitsBox)
        config_layout.addWidget(self.connectButton)
        config_layout.addWidget(self.disconnectButton)

        config_toggle_layout.addWidget(self.serialGroup)

        # Toggle checkboxes horizontal layout
        toggle_and_comm_layout = QVBoxLayout()
        checkbox_container = QGroupBox("Toggle Plot Lines")
        checkbox_layout = QGridLayout(checkbox_container)
        self.checkboxLayout = checkbox_layout
        toggle_and_comm_layout.addWidget(checkbox_container)

        # Serial Communication frame
        comm_frame = QGroupBox("Serial Communication")
        comm_layout = QHBoxLayout()
        self.sendBox = QLineEdit()
        self.sendBox.setPlaceholderText("Enter data to send...")
        self.sendButton = QPushButton("Send")
        comm_layout.addWidget(self.sendBox)
        comm_layout.addWidget(self.sendButton)
        comm_frame.setLayout(comm_layout)
        toggle_and_comm_layout.addWidget(comm_frame)

        config_toggle_layout.addLayout(toggle_and_comm_layout)

        self.data_buffers = defaultdict(lambda: {"x": [], "y": []})
        self.curves = {}
        self.checkboxes = {}

        self.reader = SerialReader()
        self.reader.new_data.connect(self.handle_new_data)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

        self.setup_ui()

    def setup_ui(self):
        self.refresh_ports()
        self.baudBox.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.baudBox.setCurrentText("115200")
        self.parityBox.addItems(["None", "Even", "Odd"])
        self.databitsBox.addItems(["5", "6", "7", "8"])
        self.databitsBox.setCurrentText("8")
        self.stopbitsBox.addItems(["1", "1.5", "2"])

        self.refreshButton.clicked.connect(self.refresh_ports)
        self.connectButton.clicked.connect(self.connect_serial)
        self.disconnectButton.clicked.connect(self.disconnect_serial)
        self.sendButton.clicked.connect(self.send_serial)
        self.sendBox.returnPressed.connect(self.send_serial)

    def refresh_ports(self):
        self.portBox.clear()
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.portBox.addItems(ports)

    def connect_serial(self):
        port = self.portBox.currentText()
        baudrate = int(self.baudBox.currentText())
        parity_map = {"None": serial.PARITY_NONE, "Even": serial.PARITY_EVEN, "Odd": serial.PARITY_ODD}
        parity = parity_map[self.parityBox.currentText()]
        databits = int(self.databitsBox.currentText())
        stopbits_map = {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE, "2": serial.STOPBITS_TWO}
        stopbits = stopbits_map[self.stopbitsBox.currentText()]

        self.reader.start(port, baudrate, parity, databits, stopbits)

    def disconnect_serial(self):
        self.reader.stop()

    def send_serial(self):
        text = self.sendBox.text().strip()
        if text:
            self.reader.send(text)
            self.sendBox.clear()

    def handle_new_data(self, label, value):
        t = time()
        buffer = self.data_buffers[label]
        buffer["x"].append(t)
        buffer["y"].append(value)
        if len(buffer["x"]) > 1000:
            buffer["x"] = buffer["x"][-1000:]
            buffer["y"] = buffer["y"][-1000:]

        if label not in self.curves:
            self.add_curve(label)

    def add_curve(self, label):
        color = pg.intColor(len(self.curves))
        self.curves[label] = self.plotWidget.plot([], [], pen=color, name=label)
        checkbox = QCheckBox(label)
        checkbox.setChecked(True)
        checkbox.stateChanged.connect(lambda: self.toggle_curve(label))
        self.checkboxes[label] = checkbox
        row = len(self.checkboxes) // 3
        col = len(self.checkboxes) % 3
        self.checkboxLayout.addWidget(checkbox, row, col)

    def toggle_curve(self, label):
        visible = self.checkboxes[label].isChecked()
        self.curves[label].setVisible(visible)

    def update_plot(self):
        for label, buffer in self.data_buffers.items():
            if label in self.curves and self.checkboxes[label].isChecked():
                self.curves[label].setData(buffer["x"], buffer["y"])

    def closeEvent(self, event):
        self.reader.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SerialPlotter()
    win.show()
    sys.exit(app.exec())
