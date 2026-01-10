"""
Script de test pour l'API d'extraction

Ce script teste l'endpoint /api/extract avec des fichiers PDF et images.
"""

import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000/api/extract"
# Pour PythonAnywhere, utilisez : https://votre_username.pythonanywhere.com/api/extract

def test_extract_api(file_path: str):
    """
    Teste l'API d'extraction avec un fichier
    
    Args:
        file_path: Chemin vers le fichier PDF ou image
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"❌ Fichier non trouvé : {file_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"📄 Test avec : {file_path.name}")
    print(f"{'='*60}")
    
    try:
        # Ouvrir le fichier en mode binaire
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f, 'application/octet-stream')}
            
            # Envoyer la requête POST
            print("⏳ Envoi de la requête...")
            response = requests.post(API_URL, files=files, timeout=30)
        
        # Vérifier le statut
        if response.status_code == 200:
            print("✅ Succès !")
            print("\n📊 Résultat :")
            result = response.json()
            
            for key, value in result.items():
                if value:
                    print(f"  • {key}: {value}")
                else:
                    print(f"  • {key}: (non trouvé)")
        else:
            print(f"❌ Erreur {response.status_code}")
            print(f"Message : {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API")
        print("Assurez-vous que l'API est démarrée : python api.py")
    except requests.exceptions.Timeout:
        print("❌ Timeout - L'API met trop de temps à répondre")
    except Exception as e:
        print(f"❌ Erreur : {str(e)}")

def main():
    """
    Fonction principale - teste plusieurs fichiers
    """
    print("🚀 Test de l'API d'extraction")
    print("="*60)
    
    # Liste des fichiers à tester
    test_files = [
        "boa.pdf",
        "boaImg.PNG",
        "Quittance.pdf",
        "QuittancePhoto.jpg"
    ]
    
    # Tester chaque fichier
    for file_name in test_files:
        file_path = Path(__file__).parent / file_name
        if file_path.exists():
            test_extract_api(file_path)
        else:
            print(f"\n⚠️  Fichier ignoré (non trouvé) : {file_name}")
    
    print(f"\n{'='*60}")
    print("✨ Tests terminés")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
