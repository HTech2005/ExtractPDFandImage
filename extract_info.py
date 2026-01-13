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
        # 3. Fallback date partielle (JJ.MM) si près d'un mot clé (cas où l'année est coupée)
        # On suppose 2025 par défaut si on trouve JJ.MM près de "valeur", "tons", "date", "le", "credit"
        date_partial = re.search(r"(?:valeur|Date|le|crediton[gs]|tons|tons|credit)[^0-9]*(\d{2}[./, ]\d{2})\b", raw_text_norm, re.IGNORECASE)
        if date_partial:
            date_versement = date_partial.group(1).replace(" ", ".").replace("/", ".").replace(",", ".") + ".2025"

    # --- REFERENCE ---
    reference = None
    # Priorité 1 : Pattern direct BOA (YB + chiffres + / + suffixe)
    # On cherche YB ou VB ou TB ou V8 ou Y8
    ref_direct = re.search(r"([YVTB][B86]\s*\d{3,}[A-Z\d]*\s*/\s*[A-Z\d]{2,5})", raw_text_norm, re.IGNORECASE)
    if ref_direct:
        temp_ref = ref_direct.group(1).upper().replace(" ", "")
        # Normalisation prefix
        for p in ["YB", "VB", "TB"]:
            if temp_ref.startswith(p[0]):
                temp_ref = p + temp_ref[2:]
                break
        reference = temp_ref

    if not reference:
        # Priorité 2 : Après le mot clé "Référence"
        ref_match_keyword = re.search(r"R[ée]f[ée]rence\s*[:; ]+([A-Z\d./]{4,})", raw_text_norm, re.IGNORECASE)
        if ref_match_keyword:
            reference = ref_match_keyword.group(1).upper().replace(" ", "")

    if not reference:
        # Fallback context-aware (Y, Ne, CAP, etc.) - Moins prioritaire car CAP peut être trompeur
        ref_match_context = re.search(r"(?:Ref|ence|Y|Ne|Quitt|Q\.)[^A-Z\d/]*([YVTB83][B86])?\s*([A-Z\d.]{4,})\s*(?:/)\s*([A-Z\d]{2,5})", raw_text_norm, re.IGNORECASE)
        if ref_match_context:
            prefix = ref_match_context.group(1) or "YB"
            prefix = prefix.replace("8", "B").replace("6", "B")
            core = "".join(filter(str.isdigit, ref_match_context.group(2)))
            suffix = ref_match_context.group(3).upper()
            if core:
                reference = f"{prefix}{core}/{suffix}"
            else:
                reference = f"{prefix}{ref_match_context.group(2).upper()}/{suffix}"

    if not reference:
        # Dernier recours : N'importe quoi qui contient un slash (sauf payeur/motif)
        raw_slashes = re.findall(r"\b([A-Z\d.]{4,})\s*/\s*([A-Za-z\d]{2,10})\b", raw_text_norm, re.IGNORECASE)
        for r1, r2 in raw_slashes:
            if any(k in r2.upper() for k in ["QUITT", "VERS", "ESPE", "TIMB", "COTON", "COT", "BENI", "2025"]): continue
            if any(k in r1.upper() for k in ["BANABASSI", "HOUNGEEDJI", "2009", "BENIN", "ICOT", "JCOT", "RB", "RCCM", "934", "0061"]): continue
            
            clean_r2 = re.split(r"\s+", r2.strip())[0]
            if len(clean_r2) > 6: clean_r2 = clean_r2[:6]
            
            reference = f"YB{r1}/{clean_r2}".upper()
            break

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
    text_for_amt = raw_text_norm.replace('¢', '0').replace('/', '0') # Cas YB image : 1¢,000 -> 10,000, 10/000 -> 10000
    text_for_amt = re.sub(r"cap[ti]?tal\s+de\s+[0-9\s.]{5,}", " CAPITAL ", text_for_amt, flags=re.IGNORECASE)
    text_for_amt = re.sub(r"(?:\+229|229|01\s*21)\s*[0-9\s-]{6,15}", " PHONE ", text_for_amt)

    # Récupérer tous les nombres entre 500 et 2M
    all_num_matches = re.findall(r"\b[0-9\s.,]{3,15}\b", text_for_amt)
    candidates = []
    # Liste de bruits à ignorer (BP, etc)
    noise = ["2009", "2003", "229", "0879", "0061"] 
    for nm in all_num_matches:
        clean = "".join(filter(str.isdigit, nm))
        if clean and 500 <= int(clean) <= 2000000 and clean not in noise:
            candidates.append(clean)
    
    if candidates:
        from collections import Counter
        counts = Counter(candidates)
        # On définit un score pour chaque candidat
        scores = {}
        for val, count in counts.items():
            # Score de base = fréquence
            score = count * 10
            # Bonus si finit par 000 ou 500 (très probable pour BOA)
            if val.endswith("000") or val.endswith("500"):
                score += 50
            
            # Bonus TRÈS fort si près de XOF ou de "votre compte"
            # On cherche dans le texte original (nettoyé des espaces multiples)
            if re.search(r"XOF\s*" + re.escape(val), text_for_amt, re.IGNORECASE) or \
               re.search(re.escape(val) + r"\s*majore", text_for_amt, re.IGNORECASE) or \
               re.search(r"compte\s*No[^0-9]*de[^0-9]*" + re.escape(val), text_for_amt, re.IGNORECASE):
                score += 100
            
            # Pénalité si présent dans une ligne de bruit (footer)
            # On cherche si le nombre est près de mots clés du footer
            if re.search(r"(?:RCCM|IFU|SWIFT|0879|934|0061)[^0-9]*" + re.escape(val), text_for_amt, re.IGNORECASE):
                score -= 80

            scores[val] = score

        # On prend le meilleur score. Si égalité, on prend la valeur la plus grande (total plus probable que timbre)
        sorted_scores = sorted(scores.items(), key=lambda x: (-x[1], -int(x[0])))
        
        # On vérifie aussi si un candidat est après "compte No" via regex directe
        compte_line_match = re.search(r"compte\s*(?:No'|No|No°|No’)\s*\d{10,13}[^0-9]*de[^0-9]*([0-9\s.,]{3,15})", text_for_amt, re.IGNORECASE)
        if compte_line_match:
            clean_compte_amt = "".join(filter(str.isdigit, compte_line_match.group(1).replace(",", "")))
            if clean_compte_amt in candidates:
                montant_val = clean_compte_amt
        
        if not montant_val:
            montant_val = sorted_scores[0][0]

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
