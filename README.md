# ExtractPDFandImage

Ce projet est un outil en Python permettant d'extraire des informations structurées à partir de quittances (reçus) au format **PDF** ou **Image (JPG/PNG)**.

Il utilise la reconnaissance optique de caractères (OCR) et l'analyse de texte pour identifier des champs spécifiques tels que le numéro de quittance, la date, le montant, etc.

## Fonctionnalités

- **Extraction PDF** : Extraction native du texte pour les PDF numériques.
- **OCR Fallback** : Si un PDF contient uniquement des images (scan), le script bascule automatiquement sur l'OCR (`pypdfium2` + `pytesseract`).
- **Upscaling Image** : Prétraitement intelligent (agrandissement, contraste, netteté) pour maximiser la précision des photos basse résolution.
- **Analyse BOA** : Optimisé pour les reçus de la **Bank Of Africa (BOA)**.
- **Extraction intelligente** : Récupère automatiquement les champs clés :
  - Date de versement
  - Référence de l'opération
  - Numéro de compte
  - Payeur
  - Motif
  - Montant (net crédité)

## Installation

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/HTech2005/ExtractPDFandImage.git
   cd ExtractPDFandImage
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Installer Tesseract OCR** (Requis pour les images et PDF scannés) :
   - Téléchargez et installez [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
   - Sur Windows, si tesseract n'est pas dans votre PATH, vous devrez peut-être décommenter la ligne dans `extract_text_from_image.py` et indiquer le chemin vers `tesseract.exe`.

## Utilisation

Le script `main.py` gère automatiquement la détection du format et le prétraitement.

```python
filename = Path("./votre_recu.pdf") # ou .png/.jpg
```

Lancez le script :
```bash
python main.py
```

## Structure du Projet

- `main.py` : Chef d'orchestre (gère le format et le prétraitement).
- `extract_info.py` : Cœur de l'intelligence (Regex et logique de nettoyage BOA).
- `extract_text_from_pdf.py` : Moteur d'extraction PDF natif.
- `extract_text_from_image.py` : Moteur OCR.
- `requirements.txt` : Liste des dépendances.


