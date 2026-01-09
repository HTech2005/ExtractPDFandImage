from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import shutil
import os
from pathlib import Path
import io
from PIL import Image

# Import existing extraction logic
from extract_text_from_pdf import extract_text_from_pdf
from extract_text_from_image import extract_text_from_image
from extract_info import extract_info_boa
# We'll use the enhanced logic from main.py
import pypdfium2 as pdfium
from PIL import ImageOps, ImageEnhance

app = FastAPI(
    title="Extraction API",
    description="API pour extraire les informations (Montant, Date, Référence, etc.) des reçus(PDF ou Image).",
    version="1.0.0"
)

class ExtractionResult(BaseModel):
    date_versement: Optional[str] = None
    reference: Optional[str] = None
    numero_compte: Optional[str] = None
    payeur: Optional[str] = None
    motif: Optional[str] = None
    montant: Optional[str] = None

def preprocess_image_api(pil_img):
    # Logique identique à main.py pour la cohérence
    img = ImageOps.grayscale(pil_img)
    img = ImageEnhance.Contrast(img).enhance(2.2)
    img = ImageEnhance.Sharpness(img).enhance(4.0)
    img = ImageOps.expand(img, border=40, fill='white')
    return img

def process_pdf_api(file_path):
    # Tentative d'extraction de texte native
    text = extract_text_from_pdf(file_path)
    if not text.strip():
        # Fallback OCR si le PDF est une image
        pdf = pdfium.PdfDocument(file_path)
        full_text = ""
        for i in range(len(pdf)):
            page = pdf[i]
            bitmap = page.render(scale=3)
            pil_img = bitmap.to_pil()
            proc_img = preprocess_image_api(pil_img)
            temp_img = f"api_temp_page_{i}.png"
            proc_img.save(temp_img)
            page_text = extract_text_from_image(temp_img, config='--psm 3')
            full_text += page_text + "\n"
            if os.path.exists(temp_img):
                os.remove(temp_img)
        pdf.close()
        text = full_text
    return text

def process_image_api(file_path):
    img = Image.open(file_path)
    # Upscaling
    w, h = img.size
    if w < 1800:
        scale_factor = 2000 / w
        img = img.resize((int(w * scale_factor), int(h * scale_factor)), Image.Resampling.LANCZOS)
    
    # Crop 2%
    w, h = img.size
    img = img.crop((int(w*0.02), int(h*0.02), int(w*0.98), int(h*0.98)))
    
    proc_img = preprocess_image_api(img)
    temp_img = "api_temp_proc.png"
    proc_img.save(temp_img)
    text = extract_text_from_image(temp_img, config='--psm 3')
    if os.path.exists(temp_img):
        os.remove(temp_img)
    return text

@app.post("/extract", response_model=ExtractionResult, summary="Extraire les données d'un reçu")
async def extract_receipt(file: UploadFile = File(...)):
    """
    Téléchargez un fichier PDF ou une Image (PNG, JPG) pour extraire les données.
    """
    extension = Path(file.filename).suffix.lower()
    if extension not in [".pdf", ".png", ".jpg", ".jpeg"]:
        raise HTTPException(status_code=400, detail="Format de fichier non supporté. Utilisez PDF, PNG ou JPG.")

    # Sauvegarder temporairement le fichier
    temp_file_path = f"api_upload_{file.filename}"
    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        if extension == ".pdf":
            raw_text = process_pdf_api(temp_file_path)
        else:
            raw_text = process_image_api(temp_file_path)
        
        infos = extract_info_boa(raw_text)
        return infos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'extraction : {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse(content={"message": "Extraction API is running. Go to /docs for Swagger documentation."})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
