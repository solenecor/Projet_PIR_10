from datetime import datetime
import sys
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from Lecture_data.lecture_mseed import lecture_mseed
from excel_export_test_param_sta_lta import run_sta_lta_and_export
from Analyse.Smoothing.wavelet import wavelet_transform
from Analyse.Smoothing.eps import eps
from Analyse.Smoothing.eppf import eppf

# 1. Chargement des données
script_dir = os.path.dirname(os.path.abspath(__file__))
full_in_path = os.path.join(script_dir, "..", "..", "..", "donnees_capteur2.mseed")
data_trace = lecture_mseed(full_in_path)

fs = data_trace[0]["sample_rate_hz"]
start_dt = datetime.strptime(data_trace[0]["start_time"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S")

# 2. Fenêtrage
window_start = datetime(2026, 5, 5, 10, 1, 0)
window_end   = datetime(2026, 5, 5, 10, 6, 50)

idx_start = int((window_start - start_dt).total_seconds() * fs)
idx_end   = int((window_end   - start_dt).total_seconds() * fs)
raw_trace = data_trace[0]["data_samples"][idx_start:idx_end]

# 3. Paramètres de test (en secondes, convertis en échantillons)
sta_seconds = [0.1, 0.25, 0.5, 1.0, 2.0]
lta_seconds = [1, 5, 10, 15, 20, 30]
thresholds  = [2, 3, 4]
wait_time   = 5

denoised_trace = eps(raw_trace, 3)

print(f"Démarrage")

# 4. Boucles imbriquées
for s_sec in sta_seconds:
    for l_sec in lta_seconds:
        for th in thresholds:
            # Conversion secondes -> échantillons
            ns = int(s_sec * fs)
            nl = int(l_sec * fs)
            
            # On vérifie que LTA > STA pour que le ratio ait du sens
            if nl > ns:
                run_sta_lta_and_export(
                    trace       = denoised_trace,
                    sample_rate = fs,
                    start_time  = window_start,
                    wait_time   = wait_time,
                    ns          = ns,
                    nl          = nl,
                    threshold   = th,
                    filepath    = "comparatif_param_STA_LTA_trace2.xlsx"
                )

print("Terminé")