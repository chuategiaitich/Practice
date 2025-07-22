import sys
import re
import serial
import serial.tools.list_ports
import threading
from threading import Lock
from time import time
from collections import defaultdict
from PyQt6.QtCore import pyqtSignal, QObject, QTimer, Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
    QLabel, QScrollArea, QFrame, QComboBox, QGroupBox, QMessageBox, QLineEdit,
    QGridLayout, QSizePolicy, QRadioButton, QStyle
)
import pyqtgraph as pg

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
                        # Split by ';' and emit each value with its index as key
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
        self.resize(1200, 600)

        main_layout = QVBoxLayout(self)

        # _____________________________ # Serial Config layout 
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
        # _____________________________ # Serial Config layout

        # _____________________________ # Plotting & Tuning layout
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
        self.step_radios[1].setChecked(True)  # Default to "1"
        PID_Tuner_layout.addWidget(self.step_group)

        def get_step():
            for radio, val in zip(self.step_radios, self.step_values):
                if radio.isChecked():
                    return val
            return 1

        Plotting_Tuning_layout.addWidget(PID_Tuner)
        
        # Plotting (right)
        self.plotWidget = pg.PlotWidget()
        self.plotWidget.showGrid(x=True, y=True)
        self.plotWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        Plotting_Tuning_layout.addWidget(self.plotWidget)
        
        # Add the combined layout to the main layout
        main_layout.addLayout(Plotting_Tuning_layout)
        # _____________________________ # Plotting & Tuning layout 

        # _____________________________ # PID tuning for D_axis
        PID_parameters = QGroupBox("D_axis")
        PID_parameters_layout = QHBoxLayout()
        PID_parameters.setLayout(PID_parameters_layout)
        main_layout.addWidget(PID_parameters)
        def make_pid_row(label_text, line_edit_attr):
            pid_row_widget = QWidget()
            pid_row_layout = QHBoxLayout(pid_row_widget)
            label = QLabel(label_text)
            line_edit = QLineEdit()
            setattr(self, line_edit_attr, line_edit)
            btn_minus = QPushButton("-")
            btn_plus = QPushButton("+")
            pid_row_layout.addWidget(label)
            pid_row_layout.addWidget(line_edit)
            pid_row_layout.addWidget(btn_minus)
            pid_row_layout.addWidget(btn_plus)
            PID_parameters_layout.addWidget(pid_row_widget)

            def change_value(delta):
                try:
                    val = float(line_edit.text())
                except ValueError:
                    val = 0.0
                step = get_step()
                new_val = val + delta * step
                line_edit.setText(str(round(new_val, 6)))
                self.send_command()
            btn_plus.clicked.connect(lambda: change_value(1))
            btn_minus.clicked.connect(lambda: change_value(-1))

        make_pid_row("Kp:", "D_Kp_input")
        make_pid_row("Ki:", "D_Ki_input")
        make_pid_row("Kd:", "D_Kd_input")
        self.D_Kp_input.setText("0")
        self.D_Ki_input.setText("0")
        self.D_Kd_input.setText("0")
        # _____________________________ # PID tuning for D_axis

        # _____________________________ # PID tuning for Q_axis
        PID_parameters = QGroupBox("Q_axis")
        PID_parameters_layout = QHBoxLayout()
        PID_parameters.setLayout(PID_parameters_layout)
        main_layout.addWidget(PID_parameters)
        def make_pid_row(label_text, line_edit_attr):
            pid_row_widget = QWidget()
            pid_row_layout = QHBoxLayout(pid_row_widget)
            label = QLabel(label_text)
            line_edit = QLineEdit()
            setattr(self, line_edit_attr, line_edit)
            btn_minus = QPushButton("-")
            btn_plus = QPushButton("+")
            pid_row_layout.addWidget(label)
            pid_row_layout.addWidget(line_edit)
            pid_row_layout.addWidget(btn_minus)
            pid_row_layout.addWidget(btn_plus)
            PID_parameters_layout.addWidget(pid_row_widget)

            def change_value(delta):
                try:
                    val = float(line_edit.text())
                except ValueError:
                    val = 0.0
                step = get_step()
                new_val = val + delta * step
                line_edit.setText(str(round(new_val, 6)))
                self.send_command()
            btn_plus.clicked.connect(lambda: change_value(1))
            btn_minus.clicked.connect(lambda: change_value(-1))
        make_pid_row("Kp:", "Q_Kp_input")
        make_pid_row("Ki:", "Q_Ki_input")
        make_pid_row("Kd:", "Q_Kd_input")
        self.Q_Kp_input.setText("0")
        self.Q_Ki_input.setText("0")
        self.Q_Kd_input.setText("0")
        # _____________________________ # PID tuning for Q_axis

        # _____________________________ # Serial communication layout 
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
        # _____________________________ # Serial communication layout 

        self.reader = Serial_Read()
        self.reader.new_data.connect(self.handle_new_data)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(50)

        self.setup_serial()

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
            self.reader.__start__(port, baudrate, parity, databits, stopbits)
            if self.reader.serial and self.reader.serial.is_open:
                QMessageBox.information(self, "Succeed", "Connected successfully!")
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
        # Store new data in buffer
        buf = self.data_buffers[key]
        timestamp = time()
        buf["x"].append(round(timestamp, 5))
        buf["y"].append(value)
        # Limit buffer size
        range = -2000
        if len(buf["x"]) > 0:
            buf["x"]  = buf["x"][range:]
            buf["y"]  = buf["y"][range:]

    def update_plot(self):
        # Plot all curves from buffer
        for key, buf in self.data_buffers.items():
            if key not in self.curves:
                color = pg.intColor(int(key), hues=len(self.data_buffers))
                self.curves[key] = self.plotWidget.plot(pen=color, name=f"Ch {key}")
            # Offset x to start at zero
            if buf["x"]:
                if buf["y"]:
                    self.curves[key].setData(buf["x"], buf["y"])  

    def send_command(self):
        # D_axis
        d_kp = self.D_Kp_input.text().strip()
        d_ki = self.D_Ki_input.text().strip()
        d_kd = self.D_Kd_input.text().strip()
        # Q_axis
        q_kp = self.Q_Kp_input.text().strip()
        q_ki = self.Q_Ki_input.text().strip()
        q_kd = self.Q_Kd_input.text().strip()

        # Send D_axis commands if values are present
        if d_kp:
            self.reader.__send__(f"DP{d_kp}")
        if d_ki:
            self.reader.__send__(f"DI{d_ki}")
        if d_kd:
            self.reader.__send__(f"DD{d_kd}")

        # Send Q_axis commands if values are present
        if q_kp:
            self.reader.__send__(f"QP{q_kp}")
        if q_ki:
            self.reader.__send__(f"QI{q_ki}")
        if q_kd:
            self.reader.__send__(f"QD{q_kd}")

    def closeEvent(self, event):
        self.reader.__stop__()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Serial_Plotter()
    win.show()
    sys.exit(app.exec())