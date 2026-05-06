from excel_export_temps_detect_sta_lta import run_and_export
from datetime import datetime
from Analyse.Smoothing.wavelet import wavelet_transform
from Lecture_data.lecture_mseed import lecture_mseed
from Analyse.Smoothing.eps import eps

trace_file = "donnees_capteur1.mseed"
data_trace = lecture_mseed(trace_file)
raw_trace = data_trace[0]["data_samples"]

start_str = data_trace[0]["start_time"]
start_dt = datetime.strptime(start_str.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")

start_str = data_trace[0]["start_time"]
start_dt = datetime.strptime(start_str.rstrip("Z"), "%Y-%m-%dT%H:%M:%S")

# Définir la fenêtre temporelle
window_start = datetime(2026, 5, 5, 10, 0, 35)
window_end   = datetime(2026, 5, 5, 10, 6, 15)

# Convertir en indices d'échantillons
fs = data_trace[0]["sample_rate_hz"]
idx_start = int((window_start - start_dt).total_seconds() * fs)
idx_end   = int((window_end   - start_dt).total_seconds() * fs)

raw_trace = data_trace[0]["data_samples"][idx_start:idx_end]

sta_list = [0.1,0.25,0.5,1.0,2.0]
lta_list = [1,5,10,20]



for threshold in [3,4]:
    for sta in sta_list:
        for lta in lta_list:
            run_and_export(
                trace       = eps(raw_trace, 1),          # ton np.ndarray
                sample_rate = data_trace[0]["sample_rate_hz"],
                sta_s       = sta,
                lta_s       = lta,
                threshold   = threshold,                   # 3 ou 4 uniquement
                wait_time   = 5,
                start_time  = window_start,
                filepath    = "Classeur1.xlsx",
            )

