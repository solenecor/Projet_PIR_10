import numpy as np
import matplotlib.pyplot as plt
import sys
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Lecture_data.lecture_mseed import lecture_mseed
import numpy as np

def compute_imer(signal, fs, n1_ms, n2_ms, n3_ms, n_avg, snr_bas):
    """
    Code IMER
    """
    # Conversion des paramètres
    n1 = max(1, int(n1_ms * fs / 1000))
    n2 = max(1, int(n2_ms * fs / 1000))
    n3 = max(1, int(n3_ms * fs / 1000))
    
    N = len(signal)
    energy = signal**2

    imer_raw = np.zeros(len(signal))
    mer12 = np.zeros(len(signal))
    mer13 = np.zeros(len(signal))


    # ETAPE 1 / CALCUL DE LA MER12 
    for k in range(n2, N - n1):
        e1 = np.mean(energy[k : k + n1])
        e2 = np.mean(energy[k - n2 : k])
        er12=e1/(e2 + 1e-10 )
        mer12[k]=er12 *(abs(signal[k]))**3


    # ETAPE 2 / CALCUL DE LA MER13
    for i in range(n3, N-n1-n2):
        e1 = np.mean(energy[i+n2 : i + n1+n2]) 
        e3 = np.mean(energy[i-n3 : i])
        er13=e1/(e3 + 1e-10)
        mer13[i]=er13 * abs(signal[i])**3

    # ETAPE 3 / Lissage de la MER12 et la MER 13
    kernel = np.ones(n_avg) / n_avg
    ma12 = np.convolve(mer12, kernel, mode='same')
    ma13 = np.convolve(mer13, kernel, mode='same')


    # ETAPE 4 / Décalage de ma13 de n2 échantillons et soustraction 
    ma13_shift=np.zeros(N)
    ma13_shift[n2:]=ma13[:N-n2]

    imer_curve = ma12 - ma13_shift

    # ETAPE 5 /  Seuillage et pointé
    debut = n2 + n3
    zone_active = imer_curve[debut:]
    indices_detection = []

    if len(zone_active) > 0:
        imer_mean= np.mean(zone_active)
        if snr_bas:
            k = 3 # Seuil plus bas pour les signaux à faible SNR
        else:
            k = 1 # Seuil standard

        threshold = imer_mean * k

        indices = np.where(zone_active > threshold)[0]
        for idx in indices:
            if len(indices_detection) == 0 or int(idx + debut) > indices_detection[-1] + fs * 10: # on attend 10s pour qu'il ne s'agisse pas du même évènement (ou alors s'il y a pas déjà d'autre détection)
                indices_detection.append(int(idx + debut)) 
        
    else:
        threshold = 0
    
    return imer_curve, threshold, indices_detection, ma12, ma13_shift


# ---UTILISATION ---
if __name__ == "__main__":
 # ---- Signal synthétique de test (décommenter pour tester sans mseed) ----
    # fs = 4000          # Hz
    # duration = 2.0     # secondes
    # t = np.linspace(0, duration, int(duration * fs))
 
    # np.random.seed(42)
    # noise = np.random.normal(0, 0.05, len(t))
 
    # arrival_time = 1.0
    # idx_arr = int(arrival_time * fs)
    # wave = np.zeros(len(t))
    # wave[idx_arr:] = (
    #     np.sin(2 * np.pi * 50 * t[idx_arr:])
    #     * np.exp(-8 * (t[idx_arr:] - arrival_time))
    # )
    # trace = noise + wave
    # -------------------------------------------------------------------------
 
    # ---- Données réelles (décommenter si lecture mseed disponible) ----------
    trace = lecture_mseed("event_CREF.mseed")[0]['data_samples']
    fs    = lecture_mseed("event_CREF.mseed")[0]['sample_rate_hz']
    t     = np.arange(len(trace)) / fs
    # -------------------------------------------------------------------------
 
    # Paramètres fenêtres (à adapter selon la durée attendue du signal)
    # Article field data : nt1=3.75 ms, nt2=nt3=15 ms
    # Article synthetic  : nt1=200 éch., nt2=nt3=600 éch. à 10 kHz
    nt1_ms  = 10    # ms — fenêtre courte
    nt2_ms  = 30    # ms — fenêtres longues (nt2 = nt3)
    nt3_ms  = 30    # ms
    n_smth  = 10    # points pour le moving average


 
    curve, thresh, pick_idx, ma12, ma13_sh = compute_imer(
        trace, fs,
        n1_ms=nt1_ms, n2_ms=nt2_ms, n3_ms=nt3_ms,
        n_avg=n_smth, snr_bas=False
    )

    if pick_idx is not None:
        print(f"Pointé IMER à : {t[pick_idx]:.4f} s  (échantillon {pick_idx})")
    else:
        print("Aucun pointé détecté.")


    ## --- Affichage ---
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    fig.suptitle("IMER — Lee et al. (2017)", fontsize=13)
 
    # Signal brut
    ax0 = axes[0]
    ax0.plot(t, trace, color='k', lw=0.7, label="Signal brut")
    if pick_idx is not None:
        ax0.axvline(t[pick_idx], color='r', lw=1.5, ls='--', label=f"Pointé IMER ({t[pick_idx]:.3f} s)")
    ax0.set_ylabel("Amplitude")
    ax0.legend(fontsize=8)
    ax0.set_title("Signal sismique")
 
    # MA₁,₂ et MA₁,₃ décalée (intermédiaires)
    ax1 = axes[1]
    ax1.plot(t, ma12,   color='steelblue', lw=1,   label="MA₁,₂")
    ax1.plot(t, ma13_sh, color='darkorange', lw=1, ls='--', label="MA₁,₃ (décalée nt2)")
    if pick_idx is not None:
        ax1.axvline(t[pick_idx], color='r', lw=1.5, ls='--')
    ax1.set_ylabel("MER lissé")
    ax1.legend(fontsize=8)
    ax1.set_title("Distributions lissées MA₁,₂ et MA₁,₃ (étape 3 & 4)")
 
    # Courbe IMER finale
    ax2 = axes[2]
    ax2.plot(t, curve, color='forestgreen', lw=1, label="IMER")
    ax2.axhline(thresh, color='orange', ls=':', lw=1.5, label=f"Seuil = mean(IMER) = {thresh:.3e}")
    if pick_idx is not None:
        ax2.axvline(t[pick_idx], color='r', lw=1.5, ls='--', label="Pointé")
    ax2.set_ylabel("IMER")
    ax2.set_xlabel("Temps (s)")
    ax2.legend(fontsize=8)
    ax2.set_title("Distribution IMER finale et seuil (étape 5)")
 
    plt.tight_layout()
    plt.show()
