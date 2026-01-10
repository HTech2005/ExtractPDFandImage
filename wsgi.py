"""
Fichier WSGI pour déployer l'API FastAPI sur PythonAnywhere

Instructions:
1. Copiez ce contenu dans votre fichier WSGI sur PythonAnywhere
   (généralement /var/www/votre_username_pythonanywhere_com_wsgi.py)
2. Remplacez 'votre_username' par votre nom d'utilisateur PythonAnywhere
3. Rechargez votre application web depuis le dashboard
"""

import sys
import os

# ==== CONFIGURATION À MODIFIER ====
# Remplacez 'votre_username' par votre nom d'utilisateur PythonAnywhere
USERNAME = 'votre_username'
PROJECT_NAME = 'ExtractPDFandImage'
VENV_NAME = 'extraction-env'
# ==================================

# Ajouter le chemin de votre projet
project_path = f'/home/{USERNAME}/{PROJECT_NAME}'
if project_path not in sys.path:
    sys.path.insert(0, project_path)

# Activer l'environnement virtuel
venv_path = f'/home/{USERNAME}/.virtualenvs/{VENV_NAME}'
activate_this = os.path.join(venv_path, 'bin', 'activate_this.py')

# Pour Python 3.6+, activate_this.py n'existe plus, on utilise cette méthode
if not os.path.exists(activate_this):
    # Méthode alternative pour activer l'environnement virtuel
    import site
    site.addsitedir(os.path.join(venv_path, 'lib', 'python3.10', 'site-packages'))
else:
    # Ancienne méthode (pour compatibilité)
    with open(activate_this) as f:
        exec(f.read(), {'__file__': activate_this})

# Importer l'application FastAPI
from api import app as application

# Configuration optionnelle pour les logs
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
