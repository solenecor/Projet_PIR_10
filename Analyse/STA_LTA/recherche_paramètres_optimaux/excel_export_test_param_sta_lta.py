import pandas as pd
import os
from datetime import timedelta
from Analyse.STA_LTA.implementation import detection_STA_LTA

def fmt_time(dt):
    """Formatage datetime → 'HH:MM:SS:cs'"""
    return dt.strftime("%H:%M:%S") + f":{dt.microsecond // 10000:02d}"

def run_sta_lta_and_export(trace, sample_rate, start_time, wait_time, ns, nl, threshold, filepath):
    # 1. Calcul de la détection
    det_indexes, ratios = detection_STA_LTA(trace, ns, nl, threshold, sample_rate, wait_time)

    # 2. Conversion des index en temps
    times = [start_time + timedelta(seconds=idx / sample_rate) for idx in det_indexes]
    
    # 3. Préparation de la ligne avec les valeurs en SECONDES
    row_data = {
        "STA (s)": ns / sample_rate,        # Conversion en secondes
        "LTA (s)": nl / sample_rate,        # Conversion en secondes
        "Threshold (Seuil)": threshold,
        "Wait time (s)": wait_time,
        "Nb Detections": len(det_indexes)
    }
    
    # Ajout des colonnes de détection (format HH:MM:SS:cs)
    for i, t in enumerate(times, start=1):
        row_data[f"Detection {i}"] = fmt_time(t)

    df_new = pd.DataFrame([row_data])

    # 4. Écriture / Ajout dans l'Excel
    if not os.path.exists(filepath):
        df_new.to_excel(filepath, index=False, sheet_name="Résultats_EPS3")
    else:
        with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            try:
                existing_df = pd.read_excel(filepath, sheet_name="Résultats_EPS3")
                start_row = len(existing_df) + 1
                header = False
            except Exception:
                start_row = 0
                header = True
            
            df_new.to_excel(writer, index=False, header=header, sheet_name="Résultats_EPS3", startrow=start_row)

    # Affichage console clair pour l'utilisateur
    print(f"   [STA={ns/sample_rate}s, LTA={nl/sample_rate}s, Seuil={threshold}] -> {len(det_indexes)} détections.")