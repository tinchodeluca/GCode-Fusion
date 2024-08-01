'''
Created on 1 ago. 2024

@author: mdelu
'''
import sys
import re
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QFileDialog

def plot_gcode_from_file(filename):
    with open(filename, 'r') as file:
        gcode = file.read().splitlines()

    current_power = 0
    x, y = 0, 0
    path = []

    for line in gcode:
        line = line.strip()
        if line.startswith(('G1', 'G3')):
            cmd = line[:2]
            matches = re.findall(r'([XYIJ])(-?\d+\.?\d*)', line)
            x_new, y_new, i, j = x, y, 0, 0
            for key, value in matches:
                if key == 'X':
                    x_new = float(value)
                elif key == 'Y':
                    y_new = float(value)
                elif key == 'I':
                    i = float(value)
                elif key == 'J':
                    j = float(value)
            path.append((x, y, x_new, y_new, current_power, cmd, i, j))
            x, y = x_new, y_new
        elif line.startswith('S'):
            current_power = int(line[1:])

    fig, ax = plt.subplots(facecolor='black')
    ax.set_facecolor('black')

    for segment in path:
        x_start, y_start, x_end, y_end, power, cmd, i, j = segment
        color = 'darkgrey' if power == 0 else 'white'
        linestyle = '--' if power == 0 or cmd == 'G3' else '-'
        linewidth = 1 if power == 0 or power < 0 else 2

        if cmd == 'G1':
            ax.plot([x_start, x_end], [y_start, y_end], color=color, linestyle=linestyle, linewidth=linewidth)
        elif cmd == 'G3':
            center_x, center_y = x_start + i, y_start + j
            radius = np.sqrt(i**2 + j**2)
            start_angle = np.arctan2(y_start - center_y, x_start - center_x)
            end_angle = np.arctan2(y_end - center_y, x_end - center_x)
            if end_angle < start_angle:
                end_angle += 2 * np.pi
            angles = np.linspace(start_angle, end_angle, 100)
            arc_x = center_x + radius * np.cos(angles)
            arc_y = center_y + radius * np.sin(angles)
            ax.plot(arc_x, arc_y, color=color, linestyle=linestyle, linewidth=linewidth)

    ax.set_aspect('equal')
    ax.set_title('G-code Path Visualization', color='white')
    ax.set_xlabel('X axis', color='white')
    ax.set_ylabel('Y axis', color='white')
    ax.tick_params(colors='white')
    plt.show()

def main():
    app = QApplication(sys.argv)
    options = QFileDialog.Options()
    filename, _ = QFileDialog.getOpenFileName(None, "Select G-code File", "", "G-code Files (*.nc);;All Files (*)", options=options)
    
    if filename:
        plot_gcode_from_file(filename)

if __name__ == "__main__":
    main()