import re

def extract_info_boa(text):
    # --- PRÉ-TRAITEMENT DU TEXTE ---
    # Normalisation agressive des espaces
    normalized_text = " ".join(text.split())
    # Garder une version brute pour certains patterns
    raw_text_norm = normalized_text.replace('’', "'").replace('°', 'O').replace('‘', "'")
    
    # --- DATE ---
    # Heuristique : Une date de versement BOA est presque toujours en 2024, 2025 ou 2026.
    date_versement = None
    # 1. Chercher une date après "valeur", "Date", "le" ou "crediton" avec année à 4 chiffres
    date_context_4d = re.search(r"(?:valeur|Date|le|crediton[gs])[^0-9]*(\d{2}[./, ]\d{2}[./, ](?:202\d))\b", raw_text_norm, re.IGNORECASE)
    if date_context_4d:
        date_versement = date_context_4d.group(1).replace(" ", ".").replace("/", ".").replace(",", ".")
    
    if not date_versement:
        # 2. Chercher JJ.MM.YYYY pur (au moins 4 chiffres pour l'année pour éviter les tels)
        date_4d = re.search(r"\b(\d{2}[./, ]\d{2}[./, ](?:202\d))\b", raw_text_norm)
        if date_4d:
            date_versement = date_4d.group(1).replace(" ", ".").replace("/", ".").replace(",", ".")
            
    if not date_versement:
        # 3. Fallback date mais UNIQUEMENT si précédé d'un mot clé (pour éviter les tels du footer)
        date_context = re.search(r"(?:valeur|Date|le|crediton[gs])[^0-9]*(\d{2}[./, ]\d{2}[./, ]\d{2,4})\b", raw_text_norm, re.IGNORECASE)
        if date_context:
            date_versement = date_context.group(1).replace(" ", ".").replace("/", ".").replace(",", ".")

    # --- REFERENCE ---
    reference = None
    # Pattern YB... (BOA) - Très flexible sur le préfixe
    # On accepte YB, VB, TB, 3B, V8, ou même rien si le pattern XXXXXX/XX est fort
    # On cherche aussi des patterns comme 24.19.2092 qui sont des misreads de YB37702
    ref_match = re.search(r"\b(?:[A-Z83]{1,2}|24\.|YB)?(\d{4,})\s*/?\s*([A-Z\d]{2,})\b", raw_text_norm, re.IGNORECASE)
    if ref_match:
        core = ref_match.group(1)
        suffix = ref_match.group(2)
        # Si ça ressemble à une date, on évite
        if not (len(core) == 2 and len(suffix) == 4):
            reference = f"YB{core}/{suffix}".upper()
    
    if not reference:
        # Autre pattern BOA : YB suivi de beaucoup de chiffres
        ref_match_yb = re.search(r"\b([A-Z83]{1,2}\d{5,})\b", raw_text_norm, re.IGNORECASE)
        if ref_match_yb:
            candidate = ref_match_yb.group(1).upper()
            if candidate.startswith(('YB', 'VB', 'TB', '3B', 'V8')):
                reference = "YB" + candidate[2:] if not candidate.startswith('YB') else candidate

    if not reference:
        # Chercher après "Référence"
        ref_match_label = re.search(r"(?:Ref[ée]rence|Ref|ence|ence:)\s*[:e]?\s*([A-Z\d/]{5,})", raw_text_norm, re.IGNORECASE)
        if ref_match_label:
            reference = ref_match_label.group(1).upper()

    # --- COMPTE ---
    # BOA account number usually starts with 01 and has 11 digits
    compte_match = re.search(r"(?:[Cc][onm]+pte|No'|No|No°|No’)[^0-9]*([01]\d{10,12})", raw_text_norm, re.IGNORECASE)
    
    # --- PAYEUR / MOTIF ---
    # On cherche tous les matches et on prend celui qui contient "QUITTANCE"
    payeur_motif_matches = re.findall(r"([A-Z\s]{5,})\s*/\s*([A-Z\s]{3,}[A-Z\d\s]*)", raw_text_norm)
    payeur = None
    motif = None
    for p, m in payeur_motif_matches:
        if "BENIN" in p and not payeur: # Fallback
            payeur, motif = p, m
        if "QUITTANCE" in m:
            payeur, motif = p, m
            break
    if not payeur and payeur_motif_matches:
        payeur, motif = payeur_motif_matches[0]
    
    # --- MONTANT ---
    montant_val = None
    # Nettoyage
    text_for_amt = re.sub(r"cap[ti]?tal\s+de\s+[0-9\s.]{5,}", " CAPITAL ", raw_text_norm, flags=re.IGNORECASE)
    text_for_amt = re.sub(r"(?:\+229|229|01\s*21)\s*[0-9\s-]{6,15}", " PHONE ", text_for_amt)

    # Stratégie 1 : Priorité absolue au montant lié au COMPTE ("compte No ... de XOF 10.000")
    # C'est généralement le montant net crédité que l'utilisateur veut.
    compte_amt_match = re.search(r"compte\s*(?:No'|No|No°|No’)\s*\d{10,13}[^0-9]*de[^0-9]*([0-9\s.,]{3,15})", text_for_amt, re.IGNORECASE)
    if compte_amt_match:
        clean = "".join(filter(str.isdigit, compte_amt_match.group(1).replace(",", "")))
        if clean and 500 <= int(clean) <= 2000000:
            montant_val = clean

    if not montant_val:
        # Stratégie 2 : Chercher le "montant initial"
        initial_amt_match = re.search(r"montant\s+initial[^0-9]*([0-9\s.,]{3,15})", text_for_amt, re.IGNORECASE)
        if initial_amt_match:
            clean = "".join(filter(str.isdigit, initial_amt_match.group(1).replace(",", "")))
            if clean and 500 <= int(clean) <= 2000000:
                montant_val = clean

    if not montant_val:
        # Stratégie 3 : "somme de" (mais c'est souvent le total avec timbre)
        somme_match = re.search(r"somme\s+de[^0-9]*([0-9\s.,]{3,15})", text_for_amt, re.IGNORECASE)
        if somme_match:
            clean = "".join(filter(str.isdigit, somme_match.group(1).replace(",", "")))
            if clean and 500 <= int(clean) <= 2000000:
                montant_val = clean

    if not montant_val:
        # Fallback global
        all_nums = re.findall(r"\b\d[0-9\s.]{3,8}\b", text_for_amt)
        potentials = [int("".join(filter(str.isdigit, n))) for n in all_nums]
        potentials = [v for v in potentials if 500 <= v <= 2000000]
        if potentials:
            # Si on n'a rien trouvé de spécifique, on prend le max
            montant_val = str(max(potentials))

    infos = {
        "date_versement": date_versement,
        "reference": reference,
        "numero_compte": compte_match.group(1) if compte_match else None,
        "payeur": payeur.strip() if payeur else None,
        "motif": motif.strip() if motif else None,
        "montant": montant_val
    }
    
    # Heuristic pour payeur/motif si non trouvés
    if not infos["payeur"]:
        payeur_alt = re.search(r"([A-Z\s]{5,})\s*/\s*(QUITTANCE|VERSEMENT)", raw_text_norm, re.IGNORECASE)
        if payeur_alt:
            infos["payeur"] = payeur_alt.group(1).strip()
            infos["motif"] = payeur_alt.group(2).strip()

    if infos["payeur"]: 
        infos["payeur"] = " ".join(infos["payeur"].split())
    if infos["motif"]: 
        # On nettoie le motif en enlevant les caractères orphelins en fin de ligne (bruit OCR)
        motif = infos["motif"]
        motif = re.split(r"Signature|BANK|Soci|RCCM|IFU", motif, flags=re.IGNORECASE)[0].strip()
        # Enlever les lettres isolées à la fin comme " S" ou " B"
        motif = re.sub(r"\s+[A-Z]$", "", motif)
        infos["motif"] = motif
        
    return infos
