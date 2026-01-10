# Guide de Déploiement sur PythonAnywhere

## ✅ Oui, vous pouvez déployer sur PythonAnywhere !

Votre API FastAPI peut être déployée sur PythonAnywhere. Voici le guide complet.

## Prérequis

- Un compte PythonAnywhere (gratuit ou payant)
- Tesseract OCR doit être installé (disponible sur les comptes payants)

> [!WARNING]
> **Limitation importante** : Le compte gratuit de PythonAnywhere ne permet pas d'installer Tesseract OCR. Vous aurez besoin d'un compte **Hacker** ($5/mois) ou supérieur pour utiliser cette API avec OCR.

## Étapes de Déploiement

### 1. Préparer votre code

Assurez-vous que tous vos fichiers sont prêts :
- `api.py` (avec les routes préfixées par `/api`)
- `requirements.txt`
- Tous les modules d'extraction (`extract_*.py`)

### 2. Créer un compte PythonAnywhere

1. Allez sur [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Créez un compte (Hacker plan recommandé pour Tesseract)

### 3. Uploader votre code

**Option A : Via Git (Recommandé)**
```bash
# Sur PythonAnywhere, ouvrez un Bash console
cd ~
git clone https://github.com/votre-username/ExtractPDFandImage.git
cd ExtractPDFandImage
```

**Option B : Upload manuel**
- Utilisez l'onglet "Files" dans le dashboard
- Uploadez tous vos fichiers Python

### 4. Installer les dépendances

Dans un Bash console sur PythonAnywhere :

```bash
# Créer un environnement virtuel
mkvirtualenv --python=/usr/bin/python3.10 extraction-env

# Activer l'environnement
workon extraction-env

# Installer les dépendances
pip install -r requirements.txt
```

### 5. Installer Tesseract OCR

> [!IMPORTANT]
> Cette étape nécessite un compte payant (Hacker ou supérieur)

```bash
# Tesseract est pré-installé sur les comptes payants
# Vérifier l'installation
which tesseract
tesseract --version
```

Si Tesseract n'est pas disponible, contactez le support PythonAnywhere.

### 6. Configurer l'application Web

1. Allez dans l'onglet **Web** du dashboard
2. Cliquez sur **Add a new web app**
3. Choisissez **Manual configuration**
4. Sélectionnez **Python 3.10**

### 7. Configurer le fichier WSGI

Éditez le fichier WSGI (par exemple `/var/www/votre_username_pythonanywhere_com_wsgi.py`) :

```python
import sys
import os

# Ajouter le chemin de votre projet
path = '/home/votre_username/ExtractPDFandImage'
if path not in sys.path:
    sys.path.insert(0, path)

# Activer l'environnement virtuel
activate_this = '/home/votre_username/.virtualenvs/extraction-env/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

# Importer l'application FastAPI
from api import app as application
```

### 8. Configurer les variables d'environnement

Dans l'onglet **Web**, section **Virtualenv** :
```
/home/votre_username/.virtualenvs/extraction-env
```

### 9. Configurer les fichiers statiques (optionnel)

Si vous avez des fichiers statiques, configurez-les dans l'onglet **Web**.

### 10. Recharger l'application

Cliquez sur le bouton vert **Reload** dans l'onglet Web.

## Tester votre API

Votre API sera accessible à :
```
https://votre_username.pythonanywhere.com/
```

Les endpoints seront :
- **Documentation** : `https://votre_username.pythonanywhere.com/docs`
- **Extraction** : `https://votre_username.pythonanywhere.com/api/extract`

### Test avec cURL

```bash
curl -X POST "https://votre_username.pythonanywhere.com/api/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@votre_fichier.pdf"
```

## Alternatives si le compte gratuit est nécessaire

Si vous devez utiliser le compte gratuit, voici des alternatives :

### Option 1 : Render.com (Gratuit avec limitations)
- Supporte Docker
- Peut installer Tesseract
- 750 heures gratuites/mois

### Option 2 : Railway.app (Gratuit avec limitations)
- $5 de crédit gratuit/mois
- Supporte Docker
- Facile à déployer

### Option 3 : Heroku (Payant)
- Buildpack Tesseract disponible
- À partir de $5/mois

### Option 4 : Google Cloud Run (Gratuit jusqu'à un certain seuil)
- Supporte Docker
- 2 millions de requêtes gratuites/mois

## Dépannage

### Erreur : "No module named 'pytesseract'"
```bash
workon extraction-env
pip install pytesseract
```

### Erreur : "Tesseract not found"
Vérifiez que vous avez un compte payant et que Tesseract est installé :
```bash
which tesseract
```

### Erreur : "Permission denied"
Assurez-vous que les permissions sont correctes :
```bash
chmod +x api.py
```

### L'API ne répond pas
- Vérifiez les logs dans l'onglet **Web** → **Log files**
- Vérifiez que l'environnement virtuel est activé
- Rechargez l'application

## Fichiers de configuration recommandés

### `.env` (pour les variables d'environnement)
```env
UPLOAD_DIR=/tmp
MAX_FILE_SIZE=10485760
```

### `runtime.txt` (optionnel)
```
python-3.10
```

## Sécurité

> [!CAUTION]
> - Ne commitez jamais vos clés API ou secrets dans Git
> - Utilisez des variables d'environnement pour les informations sensibles
> - Limitez la taille des fichiers uploadés
> - Ajoutez une authentification si nécessaire

## Support

- Documentation PythonAnywhere : [help.pythonanywhere.com](https://help.pythonanywhere.com)
- Forum PythonAnywhere : [www.pythonanywhere.com/forums](https://www.pythonanywhere.com/forums)

## Coûts

| Plan | Prix | Tesseract | Stockage | CPU |
|------|------|-----------|----------|-----|
| Beginner | Gratuit | ❌ Non | 512 MB | Limité |
| Hacker | $5/mois | ✅ Oui | 1 GB | Meilleur |
| Web Dev | $12/mois | ✅ Oui | 2 GB | Encore meilleur |

## Conclusion

PythonAnywhere est une bonne option pour déployer votre API, mais nécessite un compte payant pour Tesseract OCR. Si vous avez besoin d'une solution 100% gratuite, considérez les alternatives mentionnées ci-dessus.
