import re

def extract_info_quittance_img(text):
    # Nettoyage de certains caractères parasites
    text = text.replace('|', ' ')
    text = text.replace('‘', '')
    text = text.replace('—', '-')

    # Numéro de quittance
    numero = re.search(r"Quittance N°\s*([A-Z0-9\-\/]+)", text)
    
    # Date
    date = re.search(r"Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)
    
    # Heure
    heure = re.search(r"Quittance\s*:\s*\d{2}/\d{2}/\d{4}\s*-\s*([0-9:]+)", text)
    
    # Partie versante
    partie_versante = re.search(r"Partie\s+versante\s*:\s*(.+?)(?=Poste\s+R[ée]gie)", text, re.DOTALL)
    
    # Poste régie
    poste_regie = re.search(r"Poste\s+R[ée]gie\s*:\s*(.+?)(?=(?:\n|[A-Z0-9]{5,}\s*[-–]|Montant))", text, re.DOTALL)
    
    # Référence et libellé : chercher **après Poste Régie**
    poste_regie_end = poste_regie.end() if poste_regie else 0
    # On cherche une référence (souvent BJ...) suivie d'un tiret et du libellé
    ref_libelle_matches = re.findall(r"([A-Z0-9]{5,})\s*-\s*([^\n]+)", text[poste_regie_end:])
    
    reference = None
    libelle_reference = None
    mode_val = None

    if ref_libelle_matches:
        # On prend le dernier match après Poste Régie (souvent celui de la table)
        reference = ref_libelle_matches[-1][0].strip()
        libelle_raw = ref_libelle_matches[-1][1].strip()
        
        # Séparer le libellé du montant s'ils sont collés
        # Souvent le montant est à la fin : "Libellé 3 000"
        libelle_clean = re.sub(r"\s+\d[\d\s.,]*$", "", libelle_raw).strip()
        
        # Chercher le mode dans ce libellé
        mode_match = re.search(r"(Mobile Money|MTN MOBILE MONEY|Orange Money)", libelle_clean, re.IGNORECASE)
        if mode_match:
            mode_val = mode_match.group(0).strip()
            # Retirer le mode et les parenthèses éventuelles
            libelle_clean = libelle_clean.replace(mode_val, "").replace("()", "").replace("( )", "").strip()
        
        libelle_reference = libelle_clean
    else:
        reference = None
        libelle_reference = None
        mode_val = None
    
    # Si le mode n’a pas été trouvé dans le libellé, on cherche dans tout le texte
    if not mode_val:
        mode_search = re.search(r"(Mobile Money|MTN MOBILE MONEY|Orange Money)", text, re.IGNORECASE)
        mode_val = mode_search.group(0).strip() if mode_search else None

    # Montant versé
    montant = re.search(r"Montant\s+versé\s*([0-9\s.,]+)", text)
    montant_val = montant.group(1).replace("\n", "").replace(" ", "").replace(",", " ") if montant else None

    return {
        "numero": numero.group(1) if numero else None,
        "date": date.group(1) if date else None,
        "heure": heure.group(1) if heure else None,
        "partie_versante": partie_versante.group(1).strip() if partie_versante else None,
        "poste_regie": poste_regie.group(1).strip() if poste_regie else None,
        "reference": reference,
        "libelle_reference": libelle_reference,
        "mode": mode_val,
        "montant": montant_val
    }
