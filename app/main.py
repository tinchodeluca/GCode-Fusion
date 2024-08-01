'''
Created on 31 jul. 2024

@author: mdelu
'''
import os
import sys
import re
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QLabel, QCheckBox, QHBoxLayout,QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
import subprocess

def parse_gcode_file(file_path):
    max_speed = 0
    max_power = 0
    
    with open(file_path, 'r') as file:
        for line in file:
            speed_match = re.search(r'F(\d+(\.\d+)?)', line)
            if speed_match:
                speed = float(speed_match.group(1))
                max_speed = max(max_speed, speed)
            
            power_match = re.search(r'S(\d+(\.\d+)?)', line)
            if power_match:
                power = float(power_match.group(1))
                max_power = max(max_power, power)
    
    return {
        'filename': os.path.basename(file_path),
        'max_speed': max_speed,
        'max_power': max_power
    }

def combine_gcode_files(file_list, output_file, add_beep):
    with open(output_file, 'w') as outfile:
        for i, file_path in enumerate(file_list):
            outfile.write(f"\n(Start of file: {os.path.basename(file_path)})\n")
            
            if add_beep and i > 0:  # Add beep before each file except the first one
                outfile.write("M300 S440 P500\n")  # Beep at 440Hz for 500ms
            
            with open(file_path, 'r') as infile:
                outfile.write(infile.read())
            
            outfile.write(f"\n(End of file: {os.path.basename(file_path)})\n")
            
        if add_beep:  # Add final beep after the last file
            outfile.write("M300 S440 P500\n")  # Beep at 440Hz for 500ms

class GCodeAnalyzerCombiner(QWidget):
    def __init__(self):
        super().__init__()
        self.file_list = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.setWindowIcon(QIcon('../rsc/icon.svg'))
        
        # Title label (for PNG)
        self.title_label = QLabel(self)
        pixmap = QPixmap('../rsc/title.svg')  # Replace with your PNG file path
        scaled_pixmap = pixmap.scaled(self.width(), pixmap.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.title_label.setPixmap(scaled_pixmap)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        self.btn_select_files = QPushButton('Select G-code Files', self)
        self.btn_select_files.clicked.connect(self.select_files)
        layout.addWidget(self.btn_select_files)
        
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Filename', 'Max Speed', 'Max Power'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)
        
        # Checkboxes
        checkbox_layout = QHBoxLayout()
        self.cb_add_beep = QCheckBox('Add beep between codes')
        # self.cb_remove_travel = QCheckBox('Remove traveling to zero')
        checkbox_layout.addWidget(self.cb_add_beep)
        # checkbox_layout.addWidget(self.cb_remove_travel)
        layout.addLayout(checkbox_layout)
        
        # Combine button
        self.btn_combine = QPushButton('Combine G-code Files', self)
        self.btn_combine.clicked.connect(self.combine_files)
        layout.addWidget(self.btn_combine)
        
        self.setLayout(layout)
        self.setWindowTitle('G-code File Analyzer and Combiner')
        self.setGeometry(300, 300, 600, 500)

    def select_files(self):
        self.file_list, _ = QFileDialog.getOpenFileNames(
            self, "Select G-code files to analyze", "",
            "G-code Files (*.gcode *.nc);;All Files (*)"
        )
        
        if not self.file_list:
            print("No files selected.")
            return
        
        self.display_file_properties()

    def display_file_properties(self):
        self.table.setRowCount(0)  # Clear existing rows
        
        for file_path in self.file_list:
            properties = parse_gcode_file(file_path)
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            
            self.table.setItem(row_position, 0, QTableWidgetItem(properties['filename']))
            self.table.setItem(row_position, 1, QTableWidgetItem(f"{properties['max_speed']:.2f}"))
            self.table.setItem(row_position, 2, QTableWidgetItem(f"{properties['max_power']:.2f}"))

    def combine_files(self):
        if not self.file_list:
            print("No files selected. Please select files first.")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save combined G-code file as", "",
            "G-code Files (*.gcode *.nc);;All Files (*)"
        )
        
        if not output_file:
            print("No output file selected.")
            return
        
        add_beep = self.cb_add_beep.isChecked()
        # remove_travel = self.cb_remove_travel.isChecked()
        
        combine_gcode_files(self.file_list, output_file, add_beep)
        print(f"Combined G-code file saved as: {output_file}")
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(f"Combined G-code file saved successfully as:\n{output_file}")
        msg_box.setWindowTitle("Save Successful")
        
        open_folder_button = msg_box.addButton("Open Containing Folder", QMessageBox.ActionRole)
        msg_box.addButton(QMessageBox.Ok)
        
        msg_box.exec_()
        
        if msg_box.clickedButton() == open_folder_button:
            self.open_containing_folder(output_file)

    def open_containing_folder(self, file_path):
        folder_path = os.path.dirname(file_path)
        if os.name == 'nt':  # For Windows
            os.startfile(folder_path)
        elif os.name == 'posix':  # For macOS and Linux
            subprocess.call(['open', folder_path])
        else:
            QMessageBox.warning(self, "Unsupported OS", "Opening the folder is not supported on this operating system.")


def main():
    app = QApplication(sys.argv)
    ex = GCodeAnalyzerCombiner()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()