'''
Created on 31 jul. 2024

@author: mdelu
'''
import os
import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView

def parse_gcode_file(file_path):
    max_speed = 0
    max_power = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            # Check for speed (F parameter)
            speed_match = re.search(r'F(\d+(\.\d+)?)', line)
            if speed_match:
                speed = float(speed_match.group(1))
                max_speed = max(max_speed, speed)
            
            # Check for power (S parameter, assuming S is used for power)
            power_match = re.search(r'S(\d+(\.\d+)?)', line)
            if power_match:
                power = float(power_match.group(1))
                max_power = max(max_power, power)
    
    return {
        'filename': os.path.basename(file_path),
        'max_speed': max_speed,
        'max_power': max_power
    }

class GCodeAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.btn_select_files = QPushButton('Select G-code Files', self)
        self.btn_select_files.clicked.connect(self.select_files)
        layout.addWidget(self.btn_select_files)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Filename', 'Max Speed', 'Max Power'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        self.setLayout(layout)
        self.setWindowTitle('G-code File Analyzer')
        self.setGeometry(300, 300, 600, 400)

    def select_files(self):
        file_list, _ = QFileDialog.getOpenFileNames(
            self, "Select G-code files to analyze", "",
            "G-code Files (*.gcode *.nc);;All Files (*)"
        )
        
        if not file_list:
            print("No files selected.")
            return
        
        self.display_file_properties(file_list)

    def display_file_properties(self, file_list):
        self.table.setRowCount(0)  # Clear existing rows
        
        for file_path in file_list:
            properties = parse_gcode_file(file_path)
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            self.table.setItem(row_position, 0, QTableWidgetItem(properties['filename']))
            self.table.setItem(row_position, 1, QTableWidgetItem(f"{properties['max_speed']:.2f}"))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{properties['max_power']:.2f}"))

def main():
    app = QApplication(sys.argv)
    ex = GCodeAnalyzer()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()