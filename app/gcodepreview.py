'''
Created on 31 jul. 2024

@author: mdelu
'''
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.collections import LineCollection
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                             QFileDialog, QLabel)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import numpy as np

class GCodePreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('G-code Preview')
        self.setGeometry(100, 100, 800, 600)
        
        # Set window icon
        self.setWindowIcon(QIcon('../rsc/icon.svg'))  # Replace with your icon file

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title label
        title_label = QLabel(self)
        pixmap = QPixmap('../rsc/title.svg')  # Replace with your title image file
        title_label.setPixmap(pixmap)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Button to select G-code file
        self.btn_select = QPushButton('Select G-code File', self)
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)

        # Matplotlib figure
        plt.style.use('dark_background')
        self.figure, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select G-code file", "", "G-code Files (*.gcode *.nc);;All Files (*)")
        if file_path:
            self.parse_and_plot_gcode(file_path)

    def parse_and_plot_gcode(self, file_path):
        x, y = [], []
        powers, speeds = [], []
        current_x, current_y = 0, 0
        current_power, current_speed = 0, 0
        max_power, max_speed = 1, 1  # To normalize values
        segments_with_power = []
        segments_without_power = []

        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith(('G0', 'G1', 'S', 'F')):
                    parts = line.split()
                    move = False
                    for part in parts:
                        if part.startswith('X'):
                            current_x = float(part[1:])
                            move = True
                        elif part.startswith('Y'):
                            current_y = float(part[1:])
                            move = True
                        elif part.startswith('S'):
                            current_power = float(part[1:])
                            max_power = max(max_power, current_power)
                        elif part.startswith('F'):
                            current_speed = float(part[1:])
                            max_speed = max(max_speed, current_speed)
                    if move:
                        if x and y:  # Ensure there is at least one point in x and y
                            if current_power > 0:
                                segments_with_power.append(((x[-1], y[-1]), (current_x, current_y)))
                            else:
                                segments_without_power.append(((x[-1], y[-1]), (current_x, current_y)))
                        x.append(current_x)
                        y.append(current_y)
                        powers.append(current_power)
                        speeds.append(current_speed)

        # Normalize power and speed
        powers = np.array(powers) / max_power if max_power != 0 else np.array(powers)
        speeds = np.array(speeds) / max_speed if max_speed != 0 else np.array(speeds)

        # Create line collections
        lc_power = LineCollection(segments_with_power, colors='white', linewidths=1)
        lc_no_power = LineCollection(segments_without_power, colors='lightgray', linewidths=0.5)

        self.ax.clear()
        self.ax.add_collection(lc_power)
        self.ax.add_collection(lc_no_power)
        if x and y:  # Ensure there are points to set limits
            self.ax.set_xlim(min(x), max(x))
            self.ax.set_ylim(min(y), max(y))
        self.ax.set_xlabel('X axis')
        self.ax.set_ylabel('Y axis')
        self.ax.set_title(f'G-code Preview: {os.path.basename(file_path)}')
        self.ax.set_aspect('equal', 'datalim')

        # Add light grid
        self.ax.grid(True, color='gray', alpha=0.3, linestyle='--')

        self.canvas.draw()

def main():
    app = QApplication(sys.argv)
    ex = GCodePreviewWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()


