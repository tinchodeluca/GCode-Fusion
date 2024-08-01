'''
Created on 31 jul. 2024

@author: mdelu
'''
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.collections import LineCollection
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, 
                             QFileDialog, QLabel, QHBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import numpy as np

class PlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('G-code Preview Plot')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.figure, self.ax = plt.subplots(figsize=(8, 6), facecolor='#2E2E2E')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)

        self.statusBar().showMessage('X: 0.00, Y: 0.00')
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

    def on_mouse_move(self, event):
        if event.inaxes:
            x, y = event.xdata, event.ydata
            self.statusBar().showMessage(f'X: {x:.2f}, Y: {y:.2f}')

class GCodePreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plot_window = PlotWindow()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('G-code Preview')
        self.setGeometry(100, 100, 300, 100)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        self.btn_select = QPushButton('Select G-code File', self)
        self.btn_select.clicked.connect(self.select_file)
        layout.addWidget(self.btn_select)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select G-code file", "", "G-code Files (*.gcode *.nc);;All Files (*)")
        if file_path:
            self.parse_and_plot_gcode(file_path)

    def parse_and_plot_gcode(self, file_path):
        x, y = [], []
        powers = []
        current_x, current_y = 0, 0
        current_power = 0
        max_power = 1000

        def add_arc(start_x, start_y, end_x, end_y, center_x, center_y, clockwise):
            radius = np.sqrt((center_x - start_x)**2 + (center_y - start_y)**2)
            start_angle = np.arctan2(start_y - center_y, start_x - center_x)
            end_angle = np.arctan2(end_y - center_y, end_x - center_x)
            
            if clockwise:
                if end_angle > start_angle:
                    end_angle -= 2 * np.pi
            else:
                if end_angle < start_angle:
                    end_angle += 2 * np.pi
            
            angle = np.linspace(start_angle, end_angle, num=50)
            arc_x = center_x + radius * np.cos(angle)
            arc_y = center_y + radius * np.sin(angle)
            
            for ax, ay in zip(arc_x, arc_y):
                x.append(ax)
                y.append(ay)
                powers.append(current_power)

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip().upper()
                if line.startswith(('G', 'S')):
                    if line.startswith('S'):
                        current_power = min(float(line[1:]), max_power)
                    else:
                        parts = line.split()
                        command = parts[0]
                        if command in ['G0', 'G1']:
                            for part in parts[1:]:
                                if part.startswith('X'):
                                    current_x = float(part[1:])
                                elif part.startswith('Y'):
                                    current_y = float(part[1:])
                            x.append(current_x)
                            y.append(current_y)
                            powers.append(current_power)
                        elif command in ['G2', 'G3']:
                            end_x, end_y = current_x, current_y
                            center_x, center_y = current_x, current_y
                            for part in parts[1:]:
                                if part.startswith('X'):
                                    end_x = float(part[1:])
                                elif part.startswith('Y'):
                                    end_y = float(part[1:])
                                elif part.startswith('I'):
                                    center_x = current_x + float(part[1:])
                                elif part.startswith('J'):
                                    center_y = current_y + float(part[1:])
                            
                            add_arc(current_x, current_y, end_x, end_y, center_x, center_y, command == 'G2')
                            current_x, current_y = end_x, end_y

        # Normalize power
        powers = np.array(powers) / max_power

        # Create line segments
        points = np.array([x, y]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)

        # Create a color map based on power
        cmap = plt.get_cmap('inferno')
        colors = cmap(powers)

        # Set color and width based on power
        colors = np.where(powers[:, None] > 0, colors, [1, 1, 1, 0.3])  # White for moves
        linewidths = np.where(powers > 0, 2, 0.5)  # Thicker for engraving, thinner for moves

        # Create line collection
        lc = LineCollection(segments, colors=colors, linewidths=linewidths)

        ax = self.plot_window.ax
        ax.clear()
        ax.add_collection(lc)
        ax.set_facecolor('#1E1E1E')  # Dark gray background
        ax.set_xlim(min(x), max(x))
        ax.set_ylim(min(y), max(y))
        ax.set_xlabel('X axis')
        ax.set_ylabel('Y axis')
        ax.set_title(f'G-code Preview: {os.path.basename(file_path)}')
        ax.set_aspect('equal', 'datalim')
        ax.grid(True, color='gray', linestyle='--', alpha=0.5)

        # # Add colorbar
        # norm = plt.Normalize(0, max_power)
        # sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        # sm.set_array([])
        # cbar = self.plot_window.figure.colorbar(sm, ax=ax, label='Laser Power')
        # cbar.ax.yaxis.label.set_color('white')
        # cbar.ax.tick_params(color='white', labelcolor='white')

        self.plot_window.canvas.draw()
        self.plot_window.show()

def main():
    app = QApplication(sys.argv)
    ex = GCodePreviewWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()