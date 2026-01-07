# main.py

from extract_text_from_pdf import extract_text_from_pdf
from extract_text_from_image import extract_text_from_image
from extract_info import extract_info_quittance
from extract_info_img import extract_info_quittance_img
from pathlib import Path


filename = Path("./QuittancePhoto.jpg")
#filename = Path("./Quittance.pdf")
extension = filename.suffix

if extension.lower() in [".pdf"]:
    # Traiter comme PDF
    pdf_text = extract_text_from_pdf(str(filename))
    print(pdf_text)
    infos = extract_info_quittance(pdf_text)
    print("Infos PDF :", infos)
else:
    # Traiter comme image
    image_text = extract_text_from_image(str(filename))
    print(image_text)
    infos = extract_info_quittance_img(image_text)
    print("Infos Image :", infos)

