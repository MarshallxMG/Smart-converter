import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

def generate_qr_code(text, output_path):
    img = qrcode.make(text)
    img.save(output_path)

def decode_qr_code(image_path):
    img = Image.open(image_path)
    result = decode(img)
    if result:
        return result[0].data.decode("utf-8")
    return None
