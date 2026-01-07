import re

def extract_info_quittance(text):
    # Numéro de quittance
    numero = re.search(r"Quittance\s*N[°º]?\s*([A-Z0-9\-\/]+)", text)

    # Date
    date = re.search(r"Date\s*:\s*(\d{2}/\d{2}/\d{4})", text)

    # Heure
    heure = re.search(r"eQuittance\s*:\s*\d{2}/\d{2}/\d{4}\s*-\s*([0-9:]+)", text)

    # Partie versante
    partie_versante = re.search(r"Partie\s+versante\s*:\s*(.+)", text)

    # Poste Régie
    poste_regie = re.search(r"Poste\s+Régie\s*:\s*(.+)", text)

    # Référence et libellé
    # Exemple : BJ6600100100000104759707 - FAST/PRODUITS ACCESSOIRES
    ref_match = re.search(r"([A-Z0-9]{10,})\s*-\s*([A-Za-zÀ-ÿ\s/]+)", text)
    reference = ref_match.group(1).strip() if ref_match else None
    libelle_ref = ref_match.group(2).strip().split("\n")[0] if ref_match else None

    # Mode : ligne suivante ou entre parenthèses
    # Exemple : Mobile Money ou (MTN MOBILE MONEY)
    mode_match = re.search(r"\b([A-Za-z\s]+)\s+[0-9\s.,]+\s*\n*\(?(MTN MOBILE MONEY|MOOV|CELTIIS MOBILE MONEY|ORANGE MONEY)?\)?", text, re.IGNORECASE)
    if mode_match:
        # Si parenthèse existe, on prend ce qui est entre ()
        mode = mode_match.group(2) if mode_match.group(2) else mode_match.group(1).strip()
    else:
        # Recherche alternative simple
        mode_search = re.search(r"(MTN MOBILE MONEY|MOOV|CELTIIS MOBILE MONEY|ORANGE MONEY|Mobile Money)", text, re.IGNORECASE)
        mode = mode_search.group(0).strip() if mode_search else None

    # Montant
    montant = re.search(r"Montant\s+versé\s*([0-9\s.,]+)", text)
    montant_val = montant.group(1).strip() if montant else None

    return {
        "numero": numero.group(1).strip() if numero else None,
        "date": date.group(1) if date else None,
        "heure": heure.group(1) if heure else None,
        "partie_versante": partie_versante.group(1).strip() if partie_versante else None,
        "poste_regie": poste_regie.group(1).strip() if poste_regie else None,
        "reference": reference,
        "libelle_reference": libelle_ref,
        "mode": mode,
        "montant": montant_val
    }
