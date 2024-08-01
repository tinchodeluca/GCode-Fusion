'''
Created on 31 jul. 2024

@author: mdelu
'''
import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout

def combine_nc_files(file_list, output_file):
    with open(output_file, 'w') as outfile:
        for i, file_path in enumerate(file_list):
            outfile.write(f"\n(Start of file: {os.path.basename(file_path)})\n")
            outfile.write("M300 S440 P500\n")  # Beep at 440Hz for 500ms
            
            with open(file_path, 'r') as infile:
                outfile.write(infile.read())
            
            outfile.write(f"\n(End of file: {os.path.basename(file_path)})\n")

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        self.btn_select_files = QPushButton('Select NC Files', self)
        self.btn_select_files.clicked.connect(self.select_files)
        layout.addWidget(self.btn_select_files)
        
        self.setLayout(layout)
        self.setWindowTitle('NC File Combiner')
        self.setGeometry(300, 300, 300, 100)

    def select_files(self):
        file_list, _ = QFileDialog.getOpenFileNames(
            self, "Select NC files to combine", "",
            "NC Files (*.nc);;All Files (*)"
        )
        
        if not file_list:
            print("No files selected. Exiting.")
            return
        
        output_file, _ = QFileDialog.getSaveFileName(
            self, "Save combined NC file as", "",
            "NC Files (*.nc);;All Files (*)"
        )
        
        if not output_file:
            print("No output file selected. Exiting.")
            return
        
        combine_nc_files(file_list, output_file)
        print(f"Combined NC file saved as: {output_file}")

def main():
    app = QApplication(sys.argv)
    ex = FileSelector()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()