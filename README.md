# ExtractPDFandImage

Ce projet est un outil en Python permettant d'extraire des informations structurées à partir de quittances (reçus) au format **PDF** ou **Image (JPG/PNG)**.

Il utilise la reconnaissance optique de caractères (OCR) et l'analyse de texte pour identifier des champs spécifiques tels que le numéro de quittance, la date, le montant, etc.

## 🚀 Fonctionnalités

- **Extraction PDF** : Lit le contenu textuel des fichiers PDF.
- **Extraction Image** : Utilise `pytesseract` (OCR) pour extraire le texte des photos de quittances.
- **Analyse de données** : Extrait automatiquement les informations clés :
  - Numéro de quittance
  - Date et Heure
  - Partie versante
  - Poste Régie
  - Référence et Libellé
  - Mode de paiement
  - Montant

## 🛠️ Installation

1. **Cloner le projet** :
   ```bash
   git clone https://github.com/HTech2005/ExtractPDFandImage.git
   cd ExtractPDFandImage
   ```

2. **Installer les dépendances** :
   Assurez-vous d'avoir Python installé, puis exécutez :
   ```bash
   pip install pytesseract pillow pdfplumber
   ```

3. **Installer Tesseract OCR** (pour les images) :
   - Téléchargez et installez [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
   - Ajoutez le chemin de l'exécutable Tesseract à vos variables d'environnement.

## 💻 Utilisation

Le script principal est `main.py`. Il détecte automatiquement l'extension du fichier et utilise le bon moteur d'extraction.

Pour tester avec un fichier :
1. Modifiez la variable `filename` dans `main.py` :
   ```python
   filename = Path("./votre_fichier.pdf") # ou .jpg
   ```
2. Lancez le script :
   ```bash
   python main.py
   ```

## 📁 Structure du Projet

- `main.py` : Point d'entrée principal.
- `extract_text_from_pdf.py` : Logique d'extraction de texte pour les PDF.
- `extract_text_from_image.py` : Logique d'OCR pour les images.
- `extract_info.py` : Regex et logique pour parser les infos d'un texte (PDF).
- `extract_info_img.py` : Regex et logique pour parser les infos d'un texte (Image).

## 📝 Licence

Ce projet est libre d'utilisation.
