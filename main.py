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
    
    # 2. Augmenter le contraste et la netteté très agressivement
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
        bitmap = page.render(scale=3)
        pil_img = bitmap.to_pil()
        
        # Prétraitement
        proc_img = preprocess_image(pil_img)
        
        temp_img = f"temp_page_{i}.png"
        proc_img.save(temp_img)
        text = extract_text_from_image(temp_img, config='--psm 3')
        full_text += text + "\n"
        if os.path.exists(temp_img):
            os.remove(temp_img)
    pdf.close()
    return full_text

def process_image_with_scaling(image_path):
    print("Prétraitement de l'image (source)...")
    img = Image.open(image_path)
    
    # 1. Upscaling (Essentiel pour la clarté du texte fin comme la référence)
    w, h = img.size
    if w < 1800:
        scale_factor = 2000 / w
        img = img.resize((int(w * scale_factor), int(h * scale_factor)), Image.Resampling.LANCZOS)
        print(f"Image agrandie : {w}x{h} -> {img.size[0]}x{img.size[1]}")
    
    # 2. Rogner les bords pour enlever d'éventuels cadres noirs (2% de chaque côté)
    # Important pour les photos avec des bords sombres
    w, h = img.size
    img = img.crop((int(w*0.02), int(h*0.02), int(w*0.98), int(h*0.98)))

    # 3. Prétraitement unifié
    proc_img = preprocess_image(img)
    
    temp_img = "temp_proc.png"
    proc_img.save(temp_img)
    text = extract_text_from_image(temp_img, config='--psm 3')
    
    if os.path.exists(temp_img):
        os.remove(temp_img)
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
