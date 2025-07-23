import sys
import serial
import serial.tools.list_ports
from collections import defaultdict
from time import time
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                            QComboBox, QPushButton, QLabel, QLineEdit, QMessageBox, QRadioButton,QSizePolicy)
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
import pyqtgraph as pg
import threading

class Serial_Read(QObject):
    new_data = pyqtSignal(str, float)
    def __init__(self):
        super().__init__()
        self.serial = None
        self.running = False

    def __start__(self, port, baudrate, parity, databits, stopbits):
        try:
            self.serial = serial.Serial(
                port=port,
                baudrate=baudrate,
                parity=parity,
                bytesize=databits,
                stopbits=stopbits,
                timeout=0.01
            )
            self.running = True
            threading.Thread(target=self.__read_loop__, daemon=True).start()
        except Exception as e:
            QMessageBox.critical(None, "Serial Error", f"Could not open serial port:\n{e}")

    def __read_loop__(self):
        while self.running and self.serial and self.serial.is_open:
            if self.serial.in_waiting > 0:
                try:
                    line = self.serial.readline().decode("utf-8").strip()
                    if line:
                        values = line.split(";")
                        for idx, val in enumerate(values):
                            try:
                                fval = float(val)
                                self.new_data.emit(str(idx), fval)
                            except ValueError:
                                continue
                except Exception:
                    continue

    def __send__(self, data):
        if self.serial and self.serial.is_open:
            self.serial.write(data.encode("utf-8") + b"\n")

    def __stop__(self):
        self.running = False
        if self.serial and self.serial.is_open:
            self.serial.close()

class Serial_Plotter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Realtime Serial Plotter")
        self.resize(1600, 900)

        main_layout = QVBoxLayout(self)

        # Serial Config layout 
        serialGroup = QGroupBox("Serial Config")
        serialGroup_layout = QHBoxLayout()
        serialGroup.setLayout(serialGroup_layout)
        main_layout.addWidget(serialGroup)
        self.portBox = QComboBox()
        self.baudBox = QComboBox()
        self.parityBox = QComboBox()
        self.databitsBox = QComboBox()
        self.stopbitsBox = QComboBox()
        self.refreshButton = QPushButton("Refresh Ports")
        self.connectButton = QPushButton("Connect")
        self.disconnectButton = QPushButton("Disconnect")

        serialGroup_layout.addWidget(QLabel("Port:"))
        serialGroup_layout.addWidget(self.portBox)
        serialGroup_layout.addWidget(self.refreshButton)
        serialGroup_layout.addWidget(QLabel("Baudrate:"))
        serialGroup_layout.addWidget(self.baudBox)
        serialGroup_layout.addWidget(QLabel("Parity:"))
        serialGroup_layout.addWidget(self.parityBox)
        serialGroup_layout.addWidget(QLabel("Data Bits:"))
        serialGroup_layout.addWidget(self.databitsBox)
        serialGroup_layout.addWidget(QLabel("Stop Bits:"))
        serialGroup_layout.addWidget(self.stopbitsBox)
        serialGroup_layout.addWidget(self.connectButton)
        serialGroup_layout.addWidget(self.disconnectButton)

        # Plotting & Tuning layout
        Plotting_Tuning_layout = QHBoxLayout()
        
        # PID Tuner layout
        PID_Tuner = QGroupBox("PID Tuner")
        PID_Tuner_layout = QHBoxLayout()
        PID_Tuner.setLayout(PID_Tuner_layout)
        PID_Tuner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        self.step_group = QGroupBox("Step Size")
        self.step_layout = QVBoxLayout()
        self.step_group.setLayout(self.step_layout)
        self.step_group.setMaximumWidth(100)
        self.step_radios = []
        self.step_values = [10, 1, 0.1, 0.01, 0.001]
        for i, val in enumerate(self.step_values):
            radio = QRadioButton(str(val))
            self.step_layout.addWidget(radio)
            self.step_radios.append(radio)
        self.step_radios[1].setChecked(True)
        PID_Tuner_layout.addWidget(self.step_group)

        Plotting_Tuning_layout.addWidget(PID_Tuner)
        
        # Plotting (right)
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        Plotting_Tuning_layout.addWidget(self.plotWidget)
        
        main_layout.addLayout(Plotting_Tuning_layout)

        # PID tuning for D_axis
        PID_parameters = QGroupBox("D_axis")
        PID_parameters_layout = QHBoxLayout()
        PID_parameters.setLayout(PID_parameters_layout)
        main_layout.addWidget(PID_parameters)
        self.D_inputs = {}
        PID_parameters_layout.addWidget(self.make_pid_row("Kp:", "D_axis_Kp", "D_Kp"))
        PID_parameters_layout.addWidget(self.make_pid_row("Ki:", "D_axis_Ki", "D_Ki"))
        PID_parameters_layout.addWidget(self.make_pid_row("Kd:", "D_axis_Kd", "D_Kd"))
        self.D_inputs["D_axis_Kp"].setText("0")
        self.D_inputs["D_axis_Ki"].setText("0")
        self.D_inputs["D_axis_Kd"].setText("0")

        # PID tuning for Q_axis
        PID_parameters = QGroupBox("Q_axis")
        PID_parameters_layout = QHBoxLayout()
        PID_parameters.setLayout(PID_parameters_layout)
        main_layout.addWidget(PID_parameters)
        self.Q_inputs = {}
        PID_parameters_layout.addWidget(self.make_pid_row("Kp:", "Q_axis_Kp", "Q_Kp"))
        PID_parameters_layout.addWidget(self.make_pid_row("Ki:", "Q_axis_Ki", "Q_Ki"))
        PID_parameters_layout.addWidget(self.make_pid_row("Kd:", "Q_axis_Kd", "Q_Kd"))
        self.D_inputs["Q_axis_Kp"].setText("0")
        self.D_inputs["Q_axis_Ki"].setText("0")
        self.D_inputs["Q_axis_Kd"].setText("0")

        # Serial communication layout 
        Serial_communication = QGroupBox("Serial Communication")
        Serial_communication_layout = QHBoxLayout()
        Serial_communication.setLayout(Serial_communication_layout)
        main_layout.addWidget(Serial_communication)
        self.sendBox = QLineEdit()
        self.sendBox.setPlaceholderText("Enter data to send...")
        self.sendButton = QPushButton("Send")
        Serial_communication_layout.addWidget(self.sendBox)
        Serial_communication_layout.addWidget(self.sendButton)

        self.data_buffers = defaultdict(lambda: {"x": [], "y": []})
        self.curves = {}

        self.reader = Serial_Read()
        self.reader.new_data.connect(self.handle_new_data)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

        self.setup_serial()

    def make_pid_row(self, label_text, key, param_type):
        pid_row_widget = QWidget()
        pid_row_layout = QHBoxLayout(pid_row_widget)
        label = QLabel(label_text)
        line_edit = QLineEdit()
        self.D_inputs[key] = line_edit
        btn_minus = QPushButton("-")
        btn_plus = QPushButton("+")
        btn_minus.clicked.connect(lambda: self.adjust_pid_value(line_edit, param_type, False))
        btn_plus.clicked.connect(lambda: self.adjust_pid_value(line_edit, param_type, True))
        pid_row_layout.addWidget(label)
        pid_row_layout.addWidget(line_edit)
        pid_row_layout.addWidget(btn_minus)
        pid_row_layout.addWidget(btn_plus)
        return pid_row_widget

    def adjust_pid_value(self, line_edit, param_type, increment):
        # Get current step size
        step = 1
        for radio, val in zip(self.step_radios, self.step_values):
            if radio.isChecked():
                step = val
                break

        # Get current value from line edit
        try:
            current_value = float(line_edit.text())
        except ValueError:
            current_value = 0.0
        
        # Adjust value
        new_value = current_value + step if increment else current_value - step
        line_edit.setText(f"{new_value:.3f}")
        
        # Send serial command if port is open
        if self.reader.serial and self.reader.serial.is_open:
            command = f"{param_type}{new_value}"
            try:
                self.reader.__send__(command)
            except Exception as e:
                QMessageBox.critical(None, "Serial Error", f"Failed to send command: {e}")
        else:
            QMessageBox.critical(None, "Serial Error", f"Serial port not open for command: {param_type}")

    def setup_serial(self):
        self.refresh_ports()
        self.baudBox.addItems(["9600", "19200", "38400", "57600", "115200", "230400", "460800", "921600"])
        self.baudBox.setCurrentText("115200")
        self.parityBox.addItems(["None", "Even", "Odd"])
        self.parityBox.setCurrentText("None")
        self.databitsBox.addItems(["5", "6", "7", "8"])
        self.databitsBox.setCurrentText("8")
        self.stopbitsBox.addItems(["1", "1.5", "2"])
        self.stopbitsBox.setCurrentText("1")

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
        try:
            port = self.portBox.currentText()
            baudrate = int(self.baudBox.currentText())
            parity_map = {"None": serial.PARITY_NONE, "Even": serial.PARITY_EVEN, "Odd": serial.PARITY_ODD}
            parity = parity_map[self.parityBox.currentText()]
            databits = int(self.databitsBox.currentText())
            stopbits_map = {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE, "2": serial.STOPBITS_TWO}
            stopbits = stopbits_map[self.stopbitsBox.currentText()]
            self.reader.__stop__()  # Ensure any previous connection is closed
            self.reader.__start__(port, baudrate, parity, databits, stopbits)
            if self.reader.serial and self.reader.serial.is_open:
                QMessageBox.information(self, "Succeed", f"Connected successfully to {port} at {baudrate} baud.")
            else:
                raise Exception("Failed to open serial port")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Connection failed:\n{str(e)}")

    def disconnect_serial(self):
        self.reader.__stop__()
        QMessageBox.information(self, "Succeed", "Disconnected successfully!")

    def send_serial(self):
        text = self.sendBox.text().strip()
        if text:
            self.reader.__send__(text)
            self.sendBox.clear()

    def handle_new_data(self, key, value):
        buf = self.data_buffers[key]
        timestamp = time()
        buf["x"].append(round(timestamp, 5))
        buf["y"].append(value)
        range = -2000
        if len(buf["x"]) > 0:
            buf["x"] = buf["x"][range:]
            buf["y"] = buf["y"][range:]

    def update_plot(self):
        for key, buf in self.data_buffers.items():
            if key not in self.curves:
                color = pg.intColor(int(key), hues=len(self.data_buffers))
                self.curves[key] = self.plotWidget.plot(pen=color, name=f"Ch {key}")
            if buf["x"]:
                if buf["y"]:
                    self.curves[key].setData(buf["x"], buf["y"])  

    def closeEvent(self, event):
        self.reader.__stop__()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Serial_Plotter()
    win.show()
    sys.exit(app.exec())