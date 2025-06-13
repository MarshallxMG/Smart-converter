# smart_converter.py

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QTextEdit, QLabel, QHBoxLayout, QGraphicsOpacityEffect, QStackedWidget, QListWidget,
    QListWidgetItem, QFrame, QMessageBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QIcon, QPixmap
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


class SideMenu(QListWidget):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet("border: none;")
        self.setSpacing(10)
        options = ["Image to Text", "PDF to Word", "Folder to OCR PDF",
                   "QR Code Tools", "JPG ⇄ PNG"]
        for option in options:
            item = QListWidgetItem(option)
            item.setTextAlignment(Qt.AlignCenter)
            item.setFont(QFont('Segoe UI', 12, QFont.Bold))
            self.addItem(item)


class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔧 Smart Converter")
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(open(r"E:\Python Projects\Image to text\Combinear.qss").read())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)

        self.menu = SideMenu()
        self.menu.currentRowChanged.connect(self.display_tab)

        self.stack = QStackedWidget()
        self.tabs = [DropImageTab(), DropPdfTab(), FolderToPdfTab(),
                     QRCodeTab(), ImageFormatConverterTab()]
        for tab in self.tabs:
            self.stack.addWidget(tab)

        main_layout.addWidget(self.menu)
        main_layout.addWidget(self.stack)

        self.stack.setCurrentIndex(0)
        self.fade_animation(self.stack.currentWidget())

    def display_tab(self, index):
        self.stack.setCurrentIndex(index)
        self.fade_animation(self.stack.currentWidget())

    def fade_animation(self, widget):
        self.effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(self.effect)
        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


# Each tool tab implementation remains as in your previous script but now uses the QWidget base
class DropImageTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)

        self.label = QLabel("Drop or select an image for OCR")
        self.button = QPushButton("Select Image")
        self.result = QTextEdit()
        self.result.setReadOnly(True)

        self.button.clicked.connect(self.select_image)
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addWidget(self.result)

    def select_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            self.result.setText(pytesseract.image_to_string(Image.open(path)))

    def handle_dropped_files(self, files):
        for path in files:
            if path.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                self.result.setText(pytesseract.image_to_string(Image.open(path)))
                break


class DropPdfTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)

        self.label = QLabel("Drop or select a PDF to convert to Word")
        self.button = QPushButton("Select PDF")
        self.button.clicked.connect(self.select_pdf)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def select_pdf(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select PDF", "", "PDF Files (*.pdf)")
        if path:
            self.convert_pdf(path)

    def handle_dropped_files(self, files):
        for path in files:
            if path.lower().endswith(".pdf"):
                self.convert_pdf(path)
                break

    def convert_pdf(self, path):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Word File", "", "Word Files (*.docx)")
        if save_path:
            cv = Converter(path)
            cv.convert(save_path)
            cv.close()
            QMessageBox.information(self, "Done", "PDF successfully converted to Word!")


class FolderToPdfTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        self.label = QLabel("Drop or select a folder to create OCR PDF")
        self.button = QPushButton("Select Folder")
        self.button.clicked.connect(self.select_folder)
        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def select_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
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
                    text = pytesseract.image_to_string(Image.open(os.path.join(folder_path, filename)))
                    pdf.add_page()
                    pdf.set_font("Arial", size=12)
                    for line in text.splitlines():
                        pdf.cell(200, 10, txt=line, ln=True)
            pdf.output(save_path)
            QMessageBox.information(self, "PDF Created", "OCR PDF created successfully!")


class QRCodeTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        self.label = QLabel("QR Code Generator and Decoder")
        self.generate_btn = QPushButton("Generate QR Code")
        self.decode_btn = QPushButton("Decode QR Code")

        self.generate_btn.clicked.connect(self.generate_qr)
        self.decode_btn.clicked.connect(self.decode_qr)

        layout.addWidget(self.label)
        layout.addWidget(self.generate_btn)
        layout.addWidget(self.decode_btn)

    def generate_qr(self):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save QR Code", "", "PNG Files (*.png)")
        if save_path:
            content, _ = QFileDialog.getOpenFileName(self, "Select Text File", "", "Text Files (*.txt)")
            if content:
                with open(content) as f:
                    img = qrcode.make(f.read())
                    img.save(save_path)
                    QMessageBox.information(self, "QR Code", "QR Code saved!")

    def decode_qr(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select QR Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if path:
            result = decode(Image.open(path))
            if result:
                QMessageBox.information(self, "Decoded", result[0].data.decode("utf-8"))
            else:
                QMessageBox.warning(self, "Error", "No QR code found.")


class ImageFormatConverterTab(QWidget, DragDropMixin):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        self.label = QLabel("Batch convert JPG ⇄ PNG")
        btn1 = QPushButton("JPG to PNG")
        btn2 = QPushButton("PNG to JPG")
        btn1.clicked.connect(self.jpg_to_png)
        btn2.clicked.connect(self.png_to_jpg)
        layout.addWidget(self.label)
        layout.addWidget(btn1)
        layout.addWidget(btn2)

    def jpg_to_png(self):
        self.convert("*.jpg *.jpeg", ".png", "PNG")

    def png_to_jpg(self):
        self.convert("*.png", ".jpg", "JPEG")

    def convert(self, file_filter, ext, fmt):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", f"Images ({file_filter})")
        if files:
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
            if output_dir:
                for file in files:
                    base = os.path.splitext(os.path.basename(file))[0]
                    img = Image.open(file).convert("RGB")
                    img.save(os.path.join(output_dir, base + ext), fmt)
                QMessageBox.information(self, "Done", "Image conversion complete!")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Use absolute path to Combinear.qss
    qss_path = r"E:\Python Projects\Image to text\Combinear.qss"
    try:
        with open(qss_path, "r") as file:
            style = file.read()
            app.setStyleSheet(style)
    except FileNotFoundError:
        print("❌ Combinear.qss not found. Default style will be used.")

    w = ConverterApp()
    w.show()
    sys.exit(app.exec_())
