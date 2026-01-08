import re

def extract_info_boa_img(text):
    # Nettoyage de base pour OCR
    text = text.replace('|', ' ').replace('‘', '').replace('—', '-')
    
    # Date de versement
    date_match = re.search(r"Date\s*[:e]\s*(\d{2}[./]\d{2}[./]\d{4})", text, re.IGNORECASE)
    
    # Référence de paiement
    ref_match = re.search(r"(?:R[ée]f[ée]rence|ence)\s*:\s*([A-Z0-9\/]+)", text, re.IGNORECASE)
    
    # Numéro de compte
    compte_match = re.search(r"compte\s*N[o°]?\s*(\d{10,})", text, re.IGNORECASE)
    
    # Payeur et Motif
    payeur_motif_match = re.search(r"([A-Z\s]{5,})\s*/\s*(.+)", text)
    
    # Montant (XOF)
    montant_match = re.search(r"XOF\s*([0-9\s.,]+)", text)
    
    infos = {
        "date_versement": date_match.group(1) if date_match else None,
        "reference": ref_match.group(1) if ref_match else None,
        "numero_compte": compte_match.group(1) if compte_match else None,
        "payeur": payeur_motif_match.group(1).strip() if payeur_motif_match else None,
        "motif": payeur_motif_match.group(2).strip() if payeur_motif_match else None,
        "montant": montant_match.group(1).strip() if montant_match else None
    }
    
    if infos["payeur"]:
        infos["payeur"] = " ".join(infos["payeur"].split())
        
    return infos
