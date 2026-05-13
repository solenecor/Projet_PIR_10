from datetime import datetime
from excel_export_test_param_multi_window import run_multi_window_and_export
import sys
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from Lecture_data.lecture_mseed import lecture_mseed

trace_file = "donnees_capteur1.mseed"
data_trace = lecture_mseed(trace_file)
fs = data_trace[0]["sample_rate_hz"]
start_dt = datetime.strptime(data_trace[0]["start_time"].rstrip("Z"), "%Y-%m-%dT%H:%M:%S")


window_start = datetime(2026, 5, 5, 10, 0, 35)
window_end   = datetime(2026, 5, 5, 10, 6, 15)

idx_start = int((window_start - start_dt).total_seconds() * fs)
idx_end   = int((window_end   - start_dt).total_seconds() * fs)

raw_trace = data_trace[0]["data_samples"][idx_start:idx_end]

# Paramètres de test
bta_lengths = [30, 40, 50, 60, 70, 80]    # m
ata_lengths = [5, 10, 20, 30, 40]     # n
dta_lengths = [5, 10, 20, 30, 40]    # q
delays      = [2, 4, 8, 12]   # d
shifts      = [2, 5]          # p
alphas      = [2.5, 3.0, 3.5]       
snrs        = [2.5, 3.0, 3.5]

total_combis = len(bta_lengths) * len(ata_lengths) * len(dta_lengths) * len(delays) * len(shifts) * len(alphas) * len(snrs)
current_combi = 0


print(f"Démarrage")

for m in bta_lengths:
    for n in ata_lengths:
        if m <= n:
            continue
        for q in dta_lengths:
            if m <= q:
                continue
            for d in delays:
                for p in shifts:
                    for a in alphas: 
                        for s in snrs: 
                            current_combi += 1
                            print(f"[{current_combi}/{total_combis}] ", end="")
                            run_multi_window_and_export(
                                raw_trace, fs, window_start, 5, 
                                m, n, q, d, p, s, a, 
                                "comparatif_param_multi_window_trace2.xlsx"
                            )

print("Terminé")