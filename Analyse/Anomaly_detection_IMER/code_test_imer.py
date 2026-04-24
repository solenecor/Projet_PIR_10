import numpy as np
import matplotlib.pyplot as plt

def compute_imer(signal, fs, n1_ms=10, n2_ms=30, n3_ms=60, smoothing_ms=5):
    """
    Implémentation de l'IMER selon Lee et al. (2017)
    
    Paramètres:
    - signal : array numpy (amplitude de la trace)
    - fs : fréquence d'échantillonnage (Hz)
    - n1_ms, n2_ms, n3_ms : tailles des fenêtres en millisecondes
    - smoothing_ms : fenêtre de lissage final
    """
    
    # 1. Conversion des ms en nombre d'échantillons
    n1 = int(n1_ms * fs / 1000)
    n2 = int(n2_ms * fs / 1000)
    n3 = int(n3_ms * fs / 1000)
    n_smooth = int(smoothing_ms * fs / 1000)
    
    # 2. Préparation
    energy = signal**2
    imer_raw = np.zeros(len(signal))
    
    # 3. Calcul glissant des ratios
    # On commence à n3 pour avoir assez de passé pour la fenêtre de référence
    for i in range(n3, len(signal) - n1):
        # Énergie moyenne (Somme / N)
        e1 = np.mean(energy[i : i + n1]) 
        e2 = np.mean(energy[i - n2 : i])
        e3 = np.mean(energy[i - n3 : i])
    
        # Calcul IMER
        mer12 = (e1 / (e2 + 1e-10)) * np.abs(signal[i])
        mer13 = (e1 / (e3 + 1e-10)) * np.abs(signal[i])
    
        imer_raw[i] = mer12 - mer13
        
    # 4. Lissage final (Moving Average)
    if n_smooth > 1:
        kernel = np.ones(n_smooth) / n_smooth
        imer_curve = np.convolve(imer_raw, kernel, mode='same')
    else:
        imer_curve = imer_raw

    # 5. Pointage (Picking) par intersection avec la moyenne
    threshold = np.mean(imer_curve)
    # On cherche les indices où la courbe dépasse le seuil
    indices = np.where(imer_curve > threshold)[0]
    
    # On filtre pour ne garder que les détections après le début du signal utile
    pick = indices[0] if len(indices) > 0 else None
    
    return imer_curve, threshold, pick

# ---UTILISATION ---
if __name__ == "__main__":
    # Génération d'un signal de test (Bruit + Arrivée d'onde à 1.0s)
    fs = 500  # 500 Hz
    t = np.linspace(0, 2, 2*fs)
    noise = np.random.normal(0, 0.05, len(t))
    
    # Onde synthétique (onde P arrivant à t=1.0s)
    arrival_time = 1.0
    signal_wave = np.zeros(len(t))
    idx_arrival = int(arrival_time * fs)
    signal_wave[idx_arrival:] = np.sin(2 * np.pi * 30 * t[idx_arrival:]) * np.exp(-5*(t[idx_arrival:]-1))
    
    trace = noise + signal_wave

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