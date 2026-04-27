import numpy as np
import matplotlib.pyplot as plt
from lecture_mseed import lecture_mseed

import numpy as np

def compute_imer(signal, fs, n1_ms=10, n2_ms=30, n3_ms=60, smoothing_ms=10):
    """
    Code IMER
    """
    # 1. Conversion des paramètres
    n1 = int(n1_ms * fs / 1000)
    n2 = int(n2_ms * fs / 1000)
    n3 = int(n3_ms * fs / 1000)
    n_smooth = int(smoothing_ms * fs / 1000)
    
    energy = signal**2
    imer_raw = np.zeros(len(signal))
    mer12_raw = np.zeros(len(signal))
    mer13_raw = np.zeros(len(signal))
    # 2. Calcul des ratios (Moyennes d'énergie pour invariance)
    for i in range(n3+n2, len(signal) - n1):
        e1 = np.mean(energy[i : i + n1]) 
        e2 = np.mean(energy[i - n2 : i])
        e3 = np.mean(energy[i - n3 : i - n2])
        
        # Le 1e-10 évite la division par zéro si le capteur est silencieux
        mer12 = (e1 / (e2 + 1e-10)) * (np.abs(signal[i]))**3
        mer13 = (e1 / (e3 + 1e-10)) * np.abs(signal[i])**3
        

        mer12_raw[i] = mer12
        mer13_raw[i] = mer13
        #imer_raw[i] = mer12 - mer13
        
    # 3. Lissage 
    kernel = np.ones(n_smooth) / n_smooth
    mer12_avg = np.convolve(mer12_raw, kernel, mode='same')
    mer13_avg = np.convolve(mer13_raw, kernel, mode='same')

    imer_curve = mer12_avg - mer13_avg
    # 4. Pointage robuste (On évite le début instable)
    # On calcule la moyenne uniquement sur la partie calculée
    active_zone = imer_curve[n3:-n1]
    if len(active_zone) > 0:
        mu= np.mean(active_zone)


        threshold = mu * 3
        # On ne cherche le pointé qu'après l'initialisation (n3)
        indices = np.where(imer_curve[n3:] > threshold)[0]
        pick = (indices[0] + n3) if len(indices) > 0 else None
    else:
        threshold = 0
        pick = None
    
    return imer_curve, threshold, pick

# ---UTILISATION ---
if __name__ == "__main__":
 ################# TEST ############################
    # # Génération d'un signal de test (Bruit + Arrivée d'onde à 1.0s)
    # fs = 500  # 500 Hz
    # t = np.linspace(0, 2, 2*fs)
    # noise = np.random.normal(0, 0.05, len(t))
    
    # # Onde synthétique (onde P arrivant à t=1.0s)
    # arrival_time = 1.0
    # signal_wave = np.zeros(len(t))
    # idx_arrival = int(arrival_time * fs)
    # signal_wave[idx_arrival:] = np.sin(2 * np.pi * 30 * t[idx_arrival:]) * np.exp(-5*(t[idx_arrival:]-1))
    
    # trace = noise + signal_wave

######################################################


    trace = lecture_mseed("event.mseed")[0]['data_samples']
    fs = lecture_mseed("event.mseed")[0]['sample_rate_hz']
    t = np.arange(len(trace)) / fs

    # Application de l'IMER
    curve, thresh, pick_idx = compute_imer(trace, fs)
    print(f"pointé à : {t[pick_idx] if pick_idx is not None else 'Aucun pointé'} secondes")
    
    # Affichage
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 1, 1)
    plt.plot(t, trace, label="Signal Sismique Brut")
    if pick_idx:
        plt.axvline(t[pick_idx], color='r', linestyle='--', label="Pointé IMER")
    plt.legend()
    
    plt.subplot(2, 1, 2)
    plt.plot(t, curve, label="Courbe IMER", color='g')
    plt.axhline(thresh, color='orange', linestyle=':', label="Seuil (Moyenne)")
    plt.legend()
    plt.tight_layout()
    plt.show()
