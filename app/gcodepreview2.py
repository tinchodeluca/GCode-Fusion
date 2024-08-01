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
        gcode = file.read()

    # Initialize variables
    current_power = 0
    x, y = 0, 0
    path = []

    # Parse each line of the G-code
    for line in gcode.split('\n'):
        line = line.strip()
        if line.startswith('G1') or line.startswith('G3'):
            cmd = line[:2]
            # Use regex to find X, Y, I, J values
            matches = re.findall(r'([XYIJ])(-?\d+\.?\d*)', line)
            x_new, y_new = x, y
            i, j = 0, 0
            for match in matches:
                if match[0] == 'X':
                    x_new = float(match[1])
                elif match[0] == 'Y':
                    y_new = float(match[1])
                elif match[0] == 'I':
                    i = float(match[1])
                elif match[0] == 'J':
                    j = float(match[1])
            path.append((x, y, x_new, y_new, current_power, cmd, i, j))
            x, y = x_new, y_new
        elif line.startswith('S'):
            current_power = int(line[1:])

    # Plot the path
    fig, ax = plt.subplots()

    for segment in path:
        x_start, y_start, x_end, y_end, power, cmd, i, j = segment
        if power == 0:
            color = 'lightgrey'
            linestyle = '--'
            linewidth = 1
        else:
            color = plt.cm.viridis(power / 1000.0)
            linestyle = '-' if cmd == 'G1' else '--'
            linewidth = 2 if power >= 500 else 1

        if cmd == 'G1':
            ax.plot([x_start, x_end], [y_start, y_end], color=color, linestyle=linestyle, linewidth=linewidth)
        elif cmd == 'G3':
            # Calculate the center of the circle
            center_x = x_start + i
            center_y = y_start + j
            radius = np.sqrt(i**2 + j**2)
            
            # Determine the angles for the arc
            start_angle = np.arctan2(y_start - center_y, x_start - center_x)
            end_angle = np.arctan2(y_end - center_y, x_end - center_x)
            
            # Adjust angles to ensure proper direction and range
            if end_angle < start_angle:
                end_angle += 2 * np.pi
            
            angles = np.linspace(start_angle, end_angle, 100)
            arc_x = center_x + radius * np.cos(angles)
            arc_y = center_y + radius * np.sin(angles)
            
            ax.plot(arc_x, arc_y, color=color, linestyle=linestyle, linewidth=linewidth)

    ax.set_aspect('equal')
    ax.set_title('G-code Path Visualization')
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    plt.colorbar(plt.cm.ScalarMappable(cmap='viridis'), ax=ax, label='Laser Power')
    plt.show()

def main():
    app = QApplication(sys.argv)
    options = QFileDialog.Options()
    filename, _ = QFileDialog.getOpenFileName(None, "Select G-code File", "", "G-code Files (*.gcode);;All Files (*)", options=options)
    
    if filename:
        plot_gcode_from_file(filename)

if __name__ == "__main__":
    main()
