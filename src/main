import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel, QTabWidget, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PIL import Image
import pytesseract
from pdf2docx import Converter
from fpdf import FPDF
import qrcode
from pyzbar.pyzbar import decode

class DragDropMixin:
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        self.handle_dropped_files(files)

class ConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛠 Smart Converter - Full Suite")
        self.setMinimumSize(900, 600)
        self.dark_mode = False

        layout = QVBoxLayout(self)

        self.header = QLabel("🛠 Smart Converter")
        self.header.setStyleSheet("font-size: 26px; font-weight: bold; color: #333;")
        self.header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header)

        self.tabs = QTabWidget()
        self.tabs.addTab(DropImageTab(), "🖼 Image to Text")
        self.tabs.addTab(DropPdfTab(), "📄 PDF to Word")
        self.tabs.addTab(FolderToPdfTab(), "📁 Folder to PDF (OCR)")
        self.tabs.addTab(QRCodeTab(), "🔳 QR Code Tools")
        self.tabs.addTab(ImageFormatConverterTab(), "🖼 JPG ⇄ PNG")
        layout.addWidget(self.tabs)

        toggle_btn = QPushButton("🌓 Toggle Dark Mode")
        toggle_btn.clicked.connect(self.toggle_dark_mode)
        layout.addWidget(toggle_btn)

        self.setStyleSheet(self.light_stylesheet())

    def light_stylesheet(self):
        return """
            QWidget {
                background-color: #f9f9fb;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #4A90E2;
                color: white;
                padding: 12px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ab8;
            }
            QLabel, QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-size: 15px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                color: #4A90E2;
                background-color: #ffffff;
                border-bottom: 2px solid #4A90E2;
            }
        """

    def dark_stylesheet(self):
        return """
            QWidget {
                background-color: #121212;
                color: #ffffff;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #1f6feb;
                color: white;
                padding: 12px;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3883fa;
            }
            QLabel, QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #444;
                color: #f0f0f0;
                border-radius: 10px;
                padding: 12px;
                font-size: 14px;
            }
            QTabBar::tab {
                padding: 10px 20px;
                font-size: 15px;
                font-weight: bold;
                color: #bbb;
            }
            QTabBar::tab:selected {
                color: #ffffff;
                background-color: #1f1f1f;
                border-bottom: 2px solid #1f6feb;
            }
        """

    def toggle_dark_mode(self):
        if not self.dark_mode:
            self.setStyleSheet(self.dark_stylesheet())
            self.header.setStyleSheet("font-size: 26px; font-weight: bold; color: #ffffff;")
            self.dark_mode = True
        else:
            self.setStyleSheet(self.light_stylesheet())
            self.header.setStyleSheet("font-size: 26px; font-weight: bold; color: #333;")
            self.dark_mode = False

class DropImageTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)

        self.label = QLabel("Drop an image or click to select an image for OCR.")
        self.label.setWordWrap(True)

        self.button = QPushButton("Select Image")
        self.button.clicked.connect(self.select_image)

        self.result = QTextEdit()
        self.result.setReadOnly(True)

        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.result)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            text = pytesseract.image_to_string(Image.open(file_path))
            self.result.setText(text)

    def handle_dropped_files(self, files):
        for path in files:
            if path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                text = pytesseract.image_to_string(Image.open(path))
                self.result.setText(text)
                break

class DropPdfTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)

        self.label = QLabel("Select or drop a PDF file to convert to Word document.")
        self.label.setWordWrap(True)

        self.button = QPushButton("Select PDF")
        self.button.clicked.connect(self.select_pdf)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def select_pdf(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_path:
            self.convert_pdf(file_path)

    def handle_dropped_files(self, files):
        for path in files:
            if path.lower().endswith(".pdf"):
                self.convert_pdf(path)
                break

    def convert_pdf(self, file_path):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Word File", "", "Word Files (*.docx)")
        if save_path:
            cv = Converter(file_path)
            cv.convert(save_path, start=0, end=None)
            cv.close()
            QMessageBox.information(self, "Conversion Done", "✅ PDF successfully converted to Word!")

class FolderToPdfTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)

        self.label = QLabel("Select or drop a folder of images to convert to searchable OCR PDF.")
        self.label.setWordWrap(True)

        self.button = QPushButton("Select Folder")
        self.button.clicked.connect(self.select_folder)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder of Images")
        if folder_path:
            self.convert_folder_to_pdf(folder_path)

    def handle_dropped_files(self, files):
        for path in files:
            if os.path.isdir(path):
                self.convert_folder_to_pdf(path)
                break

    def convert_folder_to_pdf(self, folder_path):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save OCR PDF", "", "PDF Files (*.pdf)")
        if save_path:
            pdf = FPDF()
            pdf.set_auto_page_break(0)
            for filename in sorted(os.listdir(folder_path)):
                if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                    image_path = os.path.join(folder_path, filename)
                    text = pytesseract.image_to_string(Image.open(image_path))
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    for line in text.splitlines():
                        pdf.cell(200, 10, txt=line, ln=True)
            pdf.output(save_path)
            QMessageBox.information(self, "PDF Created", "✅ OCR PDF created successfully!")

class QRCodeTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)

        self.label = QLabel("Generate or decode QR Codes.")
        self.label.setWordWrap(True)

        self.generate_btn = QPushButton("Generate QR Code")
        self.generate_btn.clicked.connect(self.generate_qr)

        self.decode_btn = QPushButton("Decode QR Code")
        self.decode_btn.clicked.connect(self.decode_qr)

        layout.addWidget(self.label)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.decode_btn)

    def generate_qr(self):
        text, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "", "PNG Image (*.png)")
        if text:
            content, _ = QFileDialog.getOpenFileName(self, "Select Text File to Encode", "", "Text Files (*.txt)")
            if content:
                with open(content, 'r') as f:
                    data = f.read()
                    img = qrcode.make(data)
                    img.save(text)
                    QMessageBox.information(self, "QR Code Saved", "✅ QR Code generated and saved!")

    def decode_qr(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select QR Code Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            img = Image.open(file_path)
            result = decode(img)
            if result:
                decoded_data = result[0].data.decode("utf-8")
                QMessageBox.information(self, "Decoded Data", f"✅ Decoded Text: {decoded_data}")
            else:
                QMessageBox.warning(self, "Error", "❌ No QR code found or unreadable image.")

class ImageFormatConverterTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)

        self.status = QLabel("Select or drop images to convert between JPG and PNG.")
        self.status.setWordWrap(True)

        btn_jpg_to_png = QPushButton("🖼 Batch Convert JPG to PNG")
        btn_png_to_jpg = QPushButton("🖼 Batch Convert PNG to JPG")

        btn_jpg_to_png.clicked.connect(self.batch_jpg_to_png)
        btn_png_to_jpg.clicked.connect(self.batch_png_to_jpg)

        layout.addWidget(self.status)
        layout.addWidget(btn_jpg_to_png)
        layout.addWidget(btn_png_to_jpg)

    def handle_dropped_files(self, files):
        image_files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        if image_files:
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:
                for file_path in image_files:
                    image = Image.open(file_path).convert("RGB")
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    if file_path.lower().endswith((".jpg", ".jpeg")):
                        save_path = os.path.join(output_dir, base_name + ".png")
                        image.save(save_path, "PNG")
                    elif file_path.lower().endswith(".png"):
                        save_path = os.path.join(output_dir, base_name + ".jpg")
                        image.save(save_path, "JPEG")
                QMessageBox.information(self, "Conversion Complete", f"✅ Converted {len(image_files)} images!")

    def batch_jpg_to_png(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select JPG Images", "", "JPEG Images (*.jpg *.jpeg)")
        if files:
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:
                for file_path in files:
                    image = Image.open(file_path).convert("RGB")
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    save_path = os.path.join(output_dir, base_name + ".png")
                    image.save(save_path, "PNG")
                QMessageBox.information(self, "Conversion Complete", f"✅ {len(files)} JPG files converted to PNG!")

    def batch_png_to_jpg(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PNG Images", "", "PNG Images (*.png)")
        if files:
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:
                for file_path in files:
                    image = Image.open(file_path).convert("RGB")
                    base_name = os.path.splitext(os.path.basename(file_path))[0]
                    save_path = os.path.join(output_dir, base_name + ".jpg")
                    image.save(save_path, "JPEG")
                QMessageBox.information(self, "Conversion Complete", f"✅ {len(files)} PNG files converted to JPG!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec_())
