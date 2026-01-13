# main.py

from extract_text_from_pdf import extract_text_from_pdf
from extract_text_from_image import extract_text_from_image
from extract_info import extract_info_boa
from extract_info_img import extract_info_boa_img
import pypdfium2 as pdfium
from PIL import Image, ImageOps, ImageEnhance
import os
from pathlib import Path


filename = Path("./boa.pdf")
#filename = Path("./boaImg.PNG")
extension = filename.suffix

def preprocess_image(pil_img):
    # 1. Conversion en niveaux de gris
    img = ImageOps.grayscale(pil_img)
    
    # 2. Amélioration modérée (moins agressif que la binarisation)
    img = ImageEnhance.Contrast(img).enhance(2.2)
    img = ImageEnhance.Sharpness(img).enhance(4.0)
    
    # 3. Ajouter une bordure blanche fixe
    img = ImageOps.expand(img, border=40, fill='white')
    return img

def process_pdf_with_ocr(file_path):
    print("PDF texte vide, tentative OCR...")
    pdf = pdfium.PdfDocument(file_path)
    full_text = ""
    for i in range(len(pdf)):
        page = pdf[i]
        bitmap = page.render(scale=5)
        pil_img = bitmap.to_pil()
        
        # Prétraitement
        proc_img = preprocess_image(pil_img)
        
        temp_img = f"temp_page_{i}.png"
        proc_img.save(temp_img)
        text = extract_text_from_image(temp_img, config='--psm 6')
        full_text += text + "\n"
        if os.path.exists(temp_img):
            os.remove(temp_img)
    pdf.close()
    return full_text

def convert_image_to_pdf(image_path, pdf_path):
    print(f"Conversion de l'image en PDF : {image_path} -> {pdf_path}")
    img = Image.open(image_path)
    # Upscaling
    w, h = img.size
    if w < 1800:
        scale_factor = 2000 / w
        img = img.resize((int(w * scale_factor), int(h * scale_factor)), Image.Resampling.LANCZOS)
    
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    img.save(pdf_path, "PDF", resolution=300.0)

def process_image_with_scaling(image_path):
    # Cette fonction devient un wrapper vers la conversion PDF
    temp_pdf = "temp_converted.pdf"
    convert_image_to_pdf(image_path, temp_pdf)
    text = process_pdf_with_ocr(temp_pdf)
    if os.path.exists(temp_pdf):
        os.remove(temp_pdf)
    return text

if extension.lower() in [".pdf"]:
    # Traiter comme PDF
    pdf_text = extract_text_from_pdf(str(filename))
    
    if not pdf_text.strip():
        # Fallback OCR si le PDF est une image
        pdf_text = process_pdf_with_ocr(str(filename))
        infos = extract_info_boa(pdf_text)
        print("Infos PDF (via OCR) :", infos)
    else:
        print(pdf_text)
        infos = extract_info_boa(pdf_text)
        print("Infos PDF :", infos)
else:
    # Traiter comme image
    image_text = process_image_with_scaling(str(filename))
    print(image_text)
    infos = extract_info_boa(image_text)
    print("Infos Image :", infos)
