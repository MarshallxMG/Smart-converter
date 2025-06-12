from PIL import Image
import os

def convert_images(image_paths, output_dir, to_format):
    for file_path in image_paths:
        image = Image.open(file_path).convert("RGB")
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        new_ext = ".jpg" if to_format == "jpg" else ".png"
        save_path = os.path.join(output_dir, base_name + new_ext)
        image.save(save_path, "JPEG" if to_format == "jpg" else "PNG")
