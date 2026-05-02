import numpy as np
import matplotlib.pyplot as plt
import glob
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import lecture_mseed
from Analyse.Smoothing.eppf import eppf
from Analyse.Smoothing.eps import eps

import numpy as np

### ajouter temps d'execution et cout énérgetique 

def compute_imer(signal, fs,snr_bas=False):
    """
    Code IMER
    
    Paramètres
    ----------
    signal         : array-like, signal brut (1D)
    fs             : float, fréquence d'échantillonnage (Hz)
    snr_low        : bool,  True → seuil × 3  (S/N < 5, §4 article)
 
    Retourne
    --------
    imer_curve  : array, distribution IMER finale
    threshold   : float, seuil de détection
    picks       : list[int], indices de TOUS les pointés détectés
    ma12        : array, MA₁,₂ (debug)
    ma13_shifted: array, MA₁,₃ décalée (debug)
    """
    # Définition des paramètres
    N=len(signal)
    duree_s = N / fs

    #n2 = 10% de la durée totale du signal  (bon estimateur du bruit de fond)
    #borné entre 50ms et 5000ms

    n2_x = np.clip(duree_s * 1000 * 0.10, 50, 2000)
    n1_x = n2_x /3  # ratio fenêtre courte/longue, cohérent avec l'article
    nt1=round(n1_x,2)
    nt2 = round(n2_x, 2)
    nt3 = nt2       # toujours égal à n2
    n_avg = 10 # points pour le filtre moyenne mobile (4–10 selon S/N)
    
    dt_ms          = 1000 / fs
    persistance_ms_x= np.clip(n1_x / 10, 3 * dt_ms, n1_x / 4)
    persistance_ms = round(persistance_ms_x, 2)
    n1 = max(1, int(nt1 * fs / 1000))
    n2 = max(1, int(nt2 * fs / 1000))
    n3 = max(1, int(nt3 * fs / 1000))

    signal_clean = signal - np.mean(signal)  # Centrage du signal
    energy = signal_clean**2

    imer_raw = np.zeros(len(signal))
    mer12 = np.zeros(len(signal))
    mer13 = np.zeros(len(signal))


    # ETAPE 1 / CALCUL DE LA MER12 
    for k in range(n2, N - n1):
        e1 = np.mean(energy[k : k + n1])
        e2 = np.mean(energy[k - n2 : k])
        er12=e1/(e2 + 1e-10 )
        mer12[k]=er12 *(abs(signal_clean[k]))**3


    # ETAPE 2 / CALCUL DE LA MER13
    for i in range(n3, N-n1-n2):
        e1 = np.mean(energy[i+n2 : i + n1+n2]) 
        e3 = np.mean(energy[i-n3 : i])
        er13=e1/(e3 + 1e-10)
        mer13[i]=er13 * abs(signal_clean[i])**3

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
    cooldown= n2 + n3  # Période de non-détection après un pointé
    n_persist = max(1, int(persistance_ms * fs / 1000))  # Nombre d'échantillons consécutifs au-dessus du seuil pour valider un pointé



    if len(zone_active) > 0:
        imer_mean= np.mean(zone_active)
        if snr_bas:
            k = 3 # Seuil plus bas pour les signaux à faible SNR
        else:
            k = 1 # Seuil plus bas pour les signaux à faible SNR

        threshold = imer_mean * k

        above = zone_active > threshold # Tableau booléen indiquant les points au-dessus du seuil
        i=0
        picks=[]
        while i < len(above) -n_persist +1 :
            if np.all(above[i:i+n_persist] ):
                pick_abs=int(i + debut)
                picks.append(pick_abs)
                i +=cooldown
            else:  
                i += 1

        # indices = np.where(zone_active > threshold)[0]
        # if len(indices) > 0:
        #     for idx in indices:
        #         picks.append(idx+debut)
        # else:
        #     None
        # pick_idx = int(indices[0] + debut) if len(indices) > 0 else None
    
    else:
        threshold = 0
        pick = None
    
    return imer_curve, threshold, picks, ma12, ma13_shift


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
    # trace_brute = noise + wave
    # trace = eps(trace_brute, window_size=5)
    # -------------------------------------------------------------------------
 
    # ---- Données réelles (décommenter si lecture mseed disponible) ----------
    # trace_brute = lecture_mseed("GUI_20230310_090649.mseed")[0]['data_samples']
    # fs    = lecture_mseed("GUI_20230310_090649.mseed")[0]['sample_rate_hz']
    # print(f"Fréquence d'échantillonnage : {fs} Hz")
    # t     = np.arange(len(trace_brute)) / fs
    # trace = eps(trace_brute, window_size=5)
    
    # # -------------------------------------------------------------------------
    
    #---- Trace fourni par Hugo pour des test-----------------
    # data_folder = "../../trace_capteur"
    # fs = 100  # sampling rate (Hz)

    # Concatenate data from all file in the data folder
    # all_data = []
    # for fpath in sorted(glob.glob(data_folder + "/geophone_*.dat")):
    #     data = np.fromfile(fpath, dtype=np.int16)
    #     all_data.append(data)
    # trace_brute = np.array(np.concatenate(all_data), dtype=np.float64)
    # trace = eps(trace_brute, window_size=5)
    # t = np.arange(len(trace)) / fs
    #--------------------------------------------------------------

    # Paramètres fenêtres
    # D_ms = 100             # durée estimée d'une impulsion en ms — seul paramètre à fournir


    # nt1_ms  = D_ms   # ms — fenêtre courte
    # nt2_ms  = 3 * D_ms    # ms — fenêtres longues (nt2 = nt3)
    # nt3_ms  = 3 * D_ms    # ms
    # n_smth  = 10    # points pour le moving average
    # persistance_ms = max(1000/fs, nt1_ms/20)     # ms de persistance pour valider un pointé


    curve, thresh, picks, ma12, ma13_sh = compute_imer( trace, fs,snr_bas=False)

    
 
    # curve, thresh, picks, ma12, ma13_sh = compute_imer(
    #     trace, fs,
    #     n1_ms=nt1_ms, n2_ms=nt2_ms, n3_ms=nt3_ms,
    #     n_avg=n_smth, persistance_ms=persistance_ms, snr_bas=False
    # )

    if picks:
        print(f"{len(picks)} pointé(s) détecté(s)") 
        for i, p in enumerate(picks):
            print(f"Pointé {i+1} : t = {t[p]:.4f} s ")
    else:
        print("Aucun pointé détecté.")


    ## --- Affichage ---
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    fig.suptitle("IMER — Lee et al. (2017)", fontsize=13)
 
    # Signal brut
    ax0 = axes[0]
    ax0.plot(t, trace_brute, color='grey', lw=0.7, label="Signal brut")
    ax0.plot(t, trace, color='k', lw=0.7, label="Signal filtré")
    if picks:
        for p in picks:
            ax0.axvline(t[p], color='r', lw=1.5, ls='--')
        ax0.axvline(t[picks[0]], color='r', lw=1.5, ls='--', label=f"Pointés IMER")
    ax0.set_ylabel("Amplitude")
    ax0.legend(fontsize=8)
    ax0.set_title("Signal sismique")
 
    # MA₁,₂ et MA₁,₃ décalée (intermédiaires)
    ax1 = axes[1]
    ax1.plot(t, ma12,   color='steelblue', lw=1,   label="MA₁,₂")
    ax1.plot(t, ma13_sh, color='darkorange', lw=1, ls='--', label="MA₁,₃ (décalée nt2)")
    ax1.set_ylabel("MER lissé")
    ax1.legend(fontsize=8)
    ax1.set_title("Distributions lissées MA₁,₂ et MA₁,₃ (étape 3 & 4)")
 
    # Courbe IMER finale
    ax2 = axes[2]
    ax2.plot(t, curve, color='forestgreen', lw=1, label="IMER")
    ax2.axhline(thresh, color='orange', ls=':', lw=1.5, label=f"Seuil = mean(IMER) = {thresh:.3e}")
    ax2.set_ylabel("IMER")
    ax2.set_xlabel("Temps (s)")
    ax2.legend(fontsize=8)
    ax2.set_title("Distribution IMER finale et seuil (étape 5)")
 
    plt.tight_layout()
    plt.show()
