import os
from fpdf import FPDF
from PIL import Image
import pytesseract

def convert_folder_to_ocr_pdf(folder_path, output_path):
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
    pdf.output(output_path)
