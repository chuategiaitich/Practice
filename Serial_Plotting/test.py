import sys
import re
import serial
import serial.tools.list_ports
import pyqtgraph as pg
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QComboBox, 
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QLineEdit, 
                             QCheckBox, QScrollArea)
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor

class SerialPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serial Plotter")
        self.setGeometry(100, 100, 800, 600)

        # Serial port variables
        self.serial = None
        self.running = False
        self.is_paused = False
        self.max_points = 100
        self.pattern = re.compile(r">(\w+):\s*(-?\d+\.?\d*)")

        # Data storage: {label: [values]}
        self.data = {}
        self.time_data = []
        self.colors = ['b', 'r', 'g', 'y', 'c', 'm', 'w']  # Color cycle for plots

        # Main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)

        # Control panel
        self.control_layout = QHBoxLayout()
        self.layout.addLayout(self.control_layout)

        # COM port selection
        self.com_label = QLabel("COM Port:")
        self.control_layout.addWidget(self.com_label)
        self.com_combo = QComboBox()
        self.update_com_ports()
        self.control_layout.addWidget(self.com_combo)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_com_ports)
        self.control_layout.addWidget(self.refresh_button)

        # Baud rate selection
        self.baud_label = QLabel("Baud Rate:")
        self.control_layout.addWidget(self.baud_label)
        self.baud_combo = QComboBox()
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.control_layout.addWidget(self.baud_combo)

        # Plot mode selection
        self.mode_label = QLabel("Plot Mode:")
        self.control_layout.addWidget(self.mode_label)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['Single Plot', 'Multi Plot'])
        self.mode_combo.currentTextChanged.connect(self.update_plot_mode)
        self.control_layout.addWidget(self.mode_combo)

        # Start/Stop button
        self.start_stop_button = QPushButton("Start")
        self.start_stop_button.clicked.connect(self.start_stop_plotting)
        self.control_layout.addWidget(self.start_stop_button)

        # Pause/Resume button
        self.pause_resume_button = QPushButton("Pause")
        self.pause_resume_button.clicked.connect(self.pause_resume_plotting)
        self.pause_resume_button.setEnabled(False)
        self.control_layout.addWidget(self.pause_resume_button)

        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_plot)
        self.control_layout.addWidget(self.clear_button)

        # Checkbox panel (scrollable)
        self.checkbox_layout = QHBoxLayout()
        self.checkbox_widget = QWidget()
        self.checkbox_widget.setLayout(self.checkbox_layout)
        self.checkbox_scroll = QScrollArea()
        self.checkbox_scroll.setWidget(self.checkbox_widget)
        self.checkbox_scroll.setWidgetResizable(True)
        self.checkbox_scroll.setFixedHeight(50)
        self.layout.addWidget(self.checkbox_scroll)
        self.checkboxes = {}  # {label: QCheckBox}

        # Command input and send button
        self.command_layout = QHBoxLayout()
        self.layout.addLayout(self.command_layout)
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command")
        self.command_input.returnPressed.connect(self.send_command)
        self.command_layout.addWidget(self.command_input)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_command)
        self.command_layout.addWidget(self.send_button)

        # Plot area (scrollable for multi-plot)
        self.plot_area = QScrollArea()
        self.plot_area.setWidgetResizable(True)
        self.plot_widget_container = QWidget()
        self.plot_layout = QVBoxLayout()
        self.plot_widget_container.setLayout(self.plot_layout)
        self.plot_area.setWidget(self.plot_widget_container)
        self.layout.addWidget(self.plot_area)

        # Single plot widget
        self.single_plot_widget = pg.PlotWidget()
        self.single_plot_widget.setLabel('left', 'Value')
        self.single_plot_widget.setLabel('bottom', 'Time (s)')
        self.single_plot_widget.showGrid(x=True, y=True)
        self.plot_layout.addWidget(self.single_plot_widget)

        # Plot curves: {label: curve}
        self.curves = {}
        self.multi_plot_widgets = {}  # {label: PlotWidget}

        # Timer for updating plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_loop)
        self.start_time = None

        # Initialize plot mode
        self.update_plot_mode()

    def update_com_ports(self):
        self.com_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.com_combo.addItem(port.device)

    def start_stop_plotting(self):
        if not self.running:
            try:
                self.serial = serial.Serial(self.com_combo.currentText(), 
                                          int(self.baud_combo.currentText()), 
                                          timeout=1)
                self.running = True
                self.start_stop_button.setText("Stop")
                self.pause_resume_button.setEnabled(True)
                self.start_time = pg.ptime.time()
                self.timer.start(50)  # Update every 50ms
            except Exception as e:
                print(f"Error opening serial port: {e}")
        else:
            self.timer.stop()
            if self.serial:
                self.serial.close()
            self.running = False
            self.is_paused = False
            self.pause_resume_button.setText("Pause")
            self.start_stop_button.setText("Start")
            self.pause_resume_button.setEnabled(False)

    def pause_resume_plotting(self):
        self.is_paused = not self.is_paused
        self.pause_resume_button.setText("Resume" if self.is_paused else "Pause")

    def update_plot_mode(self):
        mode = self.mode_combo.currentText()
        if mode == 'Single Plot':
            self.single_plot_widget.setVisible(True)
            for widget in self.multi_plot_widgets.values():
                widget.setVisible(False)
            self.single_plot_widget.clear()
            self.curves = {label: self.single_plot_widget.plot(pen=self.colors[i % len(self.colors)], name=label)
                          for i, label in enumerate(self.data.keys())}
        else:  # Multi Plot
            self.single_plot_widget.setVisible(False)
            for label in self.data.keys():
                if label not in self.multi_plot_widgets:
                    widget = pg.PlotWidget()
                    widget.setLabel('left', label)
                    widget.setLabel('bottom', 'Time (s)')
                    widget.showGrid(x=True, y=True)
                    self.multi_plot_widgets[label] = widget
                    self.plot_layout.addWidget(widget)
                    self.curves[label] = widget.plot(pen=self.colors[list(self.data.keys()).index(label) % len(self.colors)], name=label)
                self.multi_plot_widgets[label].setVisible(True)

    def read_loop(self):
        if not self.running or not self.serial or self.serial.is_open:
            try:
                line = self.serial.readline().decode('utf-8').strip()
                matches = self.pattern.findall(line)
                for label, value in matches:
                    try:
                        value = float(value)
                        if label not in self.data:
                            self.data[label] = []
                            # Create checkbox for new label
                            checkbox = QCheckBox(label)
                            checkbox.setChecked(True)
                            self.checkboxes[label] = checkbox
                            self.checkbox_layout.addWidget(checkbox)
                            # Update plot curves
                            if self.mode_combo.currentText() == 'Single Plot':
                                self.curves[label] = self.single_plot_widget.plot(
                                    pen=self.colors[len(self.data) % len(self.colors)], name=label)
                            else:
                                widget = pg.PlotWidget()
                                widget.setLabel('left', label)
                                widget.setLabel('bottom', 'Time (s)')
                                widget.showGrid(x=True, y=True)
                                self.multi_plot_widgets[label] = widget
                                self.plot_layout.addWidget(widget)
                                self.curves[label] = widget.plot(
                                    pen=self.colors[len(self.data) % len(self.colors)], name=label)
                        if not self.is_paused:
                            self.data[label].append(value)
                            if len(self.data[label]) > self.max_points:
                                self.data[label].pop(0)
                            current_time = pg.ptime.time() - self.start_time
                            self.time_data.append(current_time)
                            if len(self.time_data) > self.max_points:
                                self.time_data.pop(0)
                            if not self.is_paused:
                                if self.checkboxes.get(label, False) and self.checkboxes[label].isChecked():
                                    if self.mode_combo.currentText() == 'Single Plot':
                                        self.curves[label].setData(self.time_data, self.data[label])
                                    else:
                                        self.curves[label].setData(self.time_data, self.data[label])
                                else:
                                    self.curves[label].setData([], [])
                    except ValueError:
                        pass
            except Exception:
                pass

    def send_command(self):
        if self.running and self.serial and not self.serial.is_open:
            command = self.command_input.text().strip()
            if command:
                try:
                    self.serial.write((command + '\n').encode('utf-8'))
                    self.command_input.clear()
                except Exception as e:
                    print(f"Error sending command: {e}")

    def clear_plot(self):
        self.data = {label: [] for label in self.data}
        self.time_data = []
        self.start_time = pg.ptime.time()
        for curve in self.curves.values():
            curve.setData([], [])
        for widget in self.multi_plot_widgets.values():
            widget.clear()

    def closeEvent(self, event):
        if self.serial and self.serial.is_open:
            self.serial.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SerialPlotter()
    window.show()
    sys.exit(app.exec())