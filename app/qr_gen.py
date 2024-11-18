'''
Created on 25 ago. 2024

@author: mdelu
'''
import sys
import qrcode
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QColorDialog, QFileDialog, QHBoxLayout
)
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtCore import Qt
from PIL import Image, ImageQt

class QRCodeGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("QR Code Generator")

        # Layouts
        layout = QVBoxLayout()
        form_layout = QVBoxLayout()

        # URL input
        self.url_label = QLabel("Enter URL:")
        self.url_input = QLineEdit()
        form_layout.addWidget(self.url_label)
        form_layout.addWidget(self.url_input)

        # Logo selection
        self.logo_label = QLabel("Select Logo (Optional):")
        self.logo_path_display = QLineEdit()
        self.logo_path_display.setReadOnly(True)
        self.logo_button = QPushButton("Browse")
        self.logo_button.clicked.connect(self.select_logo)
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path_display)
        logo_layout.addWidget(self.logo_button)
        form_layout.addWidget(self.logo_label)
        form_layout.addLayout(logo_layout)

        # Color selection
        self.fill_color = QColor("black")
        self.back_color = QColor("white")

        self.fill_color_button = QPushButton("Select Fill Color")
        self.fill_color_button.clicked.connect(self.select_fill_color)
        form_layout.addWidget(self.fill_color_button)

        self.back_color_button = QPushButton("Select Background Color")
        self.back_color_button.clicked.connect(self.select_back_color)
        form_layout.addWidget(self.back_color_button)

        # Preview QR code
        self.preview_button = QPushButton("Preview QR Code")
        self.preview_button.clicked.connect(self.preview_qr_code)
        form_layout.addWidget(self.preview_button)

        self.qr_preview = QLabel("QR Code Preview:")
        self.qr_preview.setAlignment(Qt.AlignCenter)
        layout.addLayout(form_layout)
        layout.addWidget(self.qr_preview)

        # Save QR code
        self.save_button = QPushButton("Save QR Code")
        self.save_button.clicked.connect(self.save_qr_code)
        layout.addWidget(self.save_button)

        # Set layout and show window
        self.setLayout(layout)
        self.setGeometry(200, 200, 400, 500)
        self.show()

    def select_logo(self):
        logo_path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Image Files (*.png *.jpg *.bmp)")
        if logo_path:
            self.logo_path_display.setText(logo_path)

    def select_fill_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.fill_color = color
            self.fill_color_button.setStyleSheet(f"background-color: {color.name()}")

    def select_back_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.back_color = color
            self.back_color_button.setStyleSheet(f"background-color: {color.name()}")

    def preview_qr_code(self):
        # Generate QR code
        img = self.create_qr_image()
        # Convert to QPixmap
        img_qt = self.pil_to_pixmap(img)
        # Set preview
        self.qr_preview.setPixmap(img_qt.scaled(250, 250, Qt.KeepAspectRatio))

    def create_qr_image(self):
        # Get user inputs
        data = self.url_input.text()
        fill_color = self.fill_color.name()
        back_color = self.back_color.name()
        logo_path = self.logo_path_display.text()

        # Create a basic QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGB')

        if logo_path:
            logo = Image.open(logo_path)
            logo_size = min(img.size[0] // 3, img.size[1] // 3)
            logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)
            pos = ((img.size[0] - logo_size) // 2, (img.size[1] - logo_size) // 2)
            img.paste(logo, pos, mask=logo if logo.mode == 'RGBA' else None)

        return img

    def pil_to_pixmap(self, img):
        # Convert PIL image to QPixmap using ImageQt
        img_qt = ImageQt.ImageQt(img)
        qimage = QImage(img_qt)
        pixmap = QPixmap.fromImage(qimage)
        return pixmap

    def save_qr_code(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "", "PNG Files (*.png);;All Files (*)")
        if save_path:
            img = self.create_qr_image()
            img.save(save_path)
            print(f"QR code saved as {save_path}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QRCodeGenerator()
    sys.exit(app.exec_())
