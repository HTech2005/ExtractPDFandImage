import pytesseract
from PIL import Image

# Si tu es sur Windows, indique le chemin de Tesseract ici :
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text


