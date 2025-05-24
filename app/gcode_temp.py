'''
Created on 24 nov. 2024

@author: mdelu
'''

import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QFileDialog, 
                           QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem,
                           QLabel, QHeaderView, QStyle, QHBoxLayout)
from PyQt5.QtCore import Qt

class GcodeAnalyzerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("G-code Temperature & Fan Speed Analyzer")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create header with file selection
        header_layout = QHBoxLayout()
        
        # File selection button
        self.select_button = QPushButton("Select G-code File")
        self.select_button.setIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        self.select_button.clicked.connect(self.select_file)
        header_layout.addWidget(self.select_button)
        
        # File name label
        self.file_label = QLabel("No file selected")
        header_layout.addWidget(self.file_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Summary section
        self.summary_label = QLabel("Summary:")
        self.summary_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.summary_label)
        
        # Create summary table
        self.summary_table = QTableWidget()
        self.summary_table.setColumnCount(2)
        self.summary_table.setRowCount(4)
        self.summary_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self.summary_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.summary_table.verticalHeader().setVisible(False)
        layout.addWidget(self.summary_table)
        
        # Initialize summary rows
        summary_metrics = [
            "Temperature Range",
            "Most Common Temperature",
            "Fan Speed Range",
            "Most Common Fan Speed"
        ]
        for i, metric in enumerate(summary_metrics):
            self.summary_table.setItem(i, 0, QTableWidgetItem(metric))
            self.summary_table.setItem(i, 1, QTableWidgetItem("N/A"))
        
        # Details section
        self.details_label = QLabel("Layer-by-Layer Details:")
        self.details_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.details_label)
        
        # Create details table
        self.details_table = QTableWidget()
        self.details_table.setColumnCount(3)
        self.details_table.setHorizontalHeaderLabels(["Layer", "Temperature (°C)", "Fan Speed (%)"])
        self.details_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.details_table)

    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select G-code File",
            "",
            "G-code Files (*.gcode);;All Files (*.*)"
        )
        
        if filename:
            self.file_label.setText(f"Selected file: {filename}")
            self.analyze_file(filename)

    def analyze_file(self, filename):
        result = parse_gcode_file(filename)
        
        if result:
            # Update summary table
            summary_values = [
                result['summary']['temperature_range'],
                f"{result['summary']['most_common_temp']}°C",
                result['summary']['fan_speed_range'],
                result['summary']['most_common_fan_speed']
            ]
            
            for i, value in enumerate(summary_values):
                self.summary_table.setItem(i, 1, QTableWidgetItem(str(value)))
            
            # Update details table with layer information
            layer_data = result['layer_data']
            self.details_table.setRowCount(len(layer_data))
            
            for i, data in enumerate(layer_data):
                # Add layer number
                layer_item = QTableWidgetItem(str(data['layer']))
                layer_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.details_table.setItem(i, 0, layer_item)
                
                # Add temperature
                temp_item = QTableWidgetItem(f"{data['temperature']:.1f}" if data['temperature'] is not None else "N/A")
                temp_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.details_table.setItem(i, 1, temp_item)
                
                # Add fan speed
                fan_item = QTableWidgetItem(f"{data['fan_speed']:.1f}" if data['fan_speed'] is not None else "N/A")
                fan_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.details_table.setItem(i, 2, fan_item)

def parse_gcode_file(filename):
    """
    Parse a G-code file to extract layer numbers, temperatures, and fan speeds.
    """
    layer_data = []
    temperatures = []
    fan_speeds = []
    current_temp = None
    current_fan_speed = None
    current_layer = 0
    last_z = 0.0
    
    # Regular expressions for matching commands
    temp_pattern = re.compile(r'M104\s+S(\d+\.?\d*)|M109\s+S(\d+\.?\d*)')
    fan_pattern = re.compile(r'M106\s+S(\d+\.?\d*)')
    layer_pattern = re.compile(r'G0\s+.*Z(\d*\.?\d*)|G1\s+.*Z(\d*\.?\d*)')
    
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Check for layer changes (Z height changes)
                layer_match = layer_pattern.search(line)
                if layer_match:
                    z_height = next(float(g) for g in layer_match.groups() if g is not None)
                    if z_height > last_z:
                        current_layer += 1
                        last_z = z_height
                        # Record the current state at layer change
                        if current_temp is not None or current_fan_speed is not None:
                            layer_data.append({
                                'layer': current_layer,
                                'temperature': current_temp,
                                'fan_speed': current_fan_speed
                            })
                
                # Check for temperature changes
                temp_match = temp_pattern.search(line)
                if temp_match:
                    current_temp = next(float(g) for g in temp_match.groups() if g is not None)
                    temperatures.append(current_temp)
                    # Record the change
                    layer_data.append({
                        'layer': current_layer,
                        'temperature': current_temp,
                        'fan_speed': current_fan_speed
                    })
                
                # Check for fan speed changes
                fan_match = fan_pattern.search(line)
                if fan_match:
                    fan_speed = float(fan_match.group(1))
                    if fan_speed > 1:  # If value is in 0-255 range
                        fan_speed = (fan_speed / 255) * 100
                    else:  # If value is already in 0-1 range
                        fan_speed *= 100
                    current_fan_speed = fan_speed
                    fan_speeds.append(fan_speed)
                    # Record the change
                    layer_data.append({
                        'layer': current_layer,
                        'temperature': current_temp,
                        'fan_speed': current_fan_speed
                    })
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return None
    
    # Remove duplicate consecutive entries
    filtered_data = []
    last_entry = None
    for entry in layer_data:
        if last_entry is None or \
           entry['temperature'] != last_entry['temperature'] or \
           entry['fan_speed'] != last_entry['fan_speed'] or \
           entry['layer'] != last_entry['layer']:
            filtered_data.append(entry)
            last_entry = entry
    
    return {
        'layer_data': filtered_data,
        'summary': {
            'temperature_range': f"{min(temperatures) if temperatures else 'N/A'} - {max(temperatures) if temperatures else 'N/A'}°C",
            'most_common_temp': max(set(temperatures), key=temperatures.count) if temperatures else 'N/A',
            'fan_speed_range': f"{min(fan_speeds) if fan_speeds else 'N/A'} - {max(fan_speeds) if fan_speeds else 'N/A'}%",
            'most_common_fan_speed': f"{max(set(fan_speeds), key=fan_speeds.count):.1f}%" if fan_speeds else 'N/A'
        }
    }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GcodeAnalyzerGUI()
    window.show()
    sys.exit(app.exec_())