import pandas as pd
import os
from datetime import timedelta
from openpyxl import load_workbook
# Assure-toi que le nom du fichier importé correspond au tien
from Analyse.Multi_window.implementation import detection_multi_window

def fmt_time(dt):
    """Formatage datetime → 'HH:MM:SS:cs'"""
    return dt.strftime("%H:%M:%S") + f":{dt.microsecond // 10000:02d}"

def run_multi_window_and_export(trace, sample_rate, start_time, wait_time, m, n, q, d, p, snr, alpha, filepath):
    
    # 1. Calcul de la détection[cite: 1]
    det_indexes, r2, r3, h1, h2, h3 = detection_multi_window(
        trace, m, n, q, d, p, alpha, snr, sample_rate, wait_time
    )

    # 2. Conversion des index en temps
    times = [start_time + timedelta(seconds=idx / sample_rate) for idx in det_indexes]
    
    # 3. Préparation de la ligne avec les TITRES DE COLONNES complets
    row_data = {
        "BTA window length (samples)": m,
        "Number of shifted samples (p)": p,
        "ATA window length (samples)": n,
        "DTA window length (samples)": q,
        "DTA delay (samples)": d,
        "Average value of SNR": snr,
        "Coefficient alpha": alpha,
        "Nb Detections": len(det_indexes)
    }
    
    # Ajout des colonnes de détection (Det 1, Det 2, etc.)
    for i, t in enumerate(times, start=1):
        row_data[f"Detection {i}"] = fmt_time(t)

    df_new = pd.DataFrame([row_data])

    # 4. Écriture / Ajout dans l'Excel
    if not os.path.exists(filepath):
        # Création du fichier s'il n'existe pas
        df_new.to_excel(filepath, index=False, sheet_name="results")
    else:
        # Ajout à la suite dans le fichier existant
        with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            try:
                existing_df = pd.read_excel(filepath, sheet_name="results")
                start_row = len(existing_df) + 1
                header = False
            except Exception:
                start_row = 0
                header = True
            
            df_new.to_excel(writer, index=False, header=header, sheet_name="results", startrow=start_row)

    # Affichage console pour suivi
    print(f"   [BTA={m}, shift={p}, ATA={n}, DTA={q}, delay={d}] -> {len(det_indexes)} détections.")