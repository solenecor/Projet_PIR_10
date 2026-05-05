import numpy as np
import matplotlib.pyplot as plt
import glob
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import lecture_mseed
from Analyse.Smoothing.eppf import eppf
from Analyse.Smoothing.eps import eps


def compute_mcm(signal, fs,wait_time=10, k=5):
    """
    Modified Coppens's Method (MCM) — Détection du premier mouvement.

    Basé sur : Sabbione & Velis (2010), Geophysics, 75(4), V67–V76.

    L'attribut énergie-ratio ER(t) est calculé à partir de deux fenêtres
    imbriquées : une fenêtre courte glissante (E1) et une fenêtre cumulative
    croissante (E2). L'attribut est ensuite lissé par EPS, et le pointé
    est placé au maximum de sa dérivée.

    Paramètres
    ----------
    signal : array-like, signal brut (1D)
    fs     : float, fréquence d'échantillonnage (Hz)

    Retourne
    --------
    er_raw      : array, attribut énergie-ratio brut
    er_filtered : array, attribut lissé par EPS
    derivative  : array, dérivée de l'attribut filtré
    pick        : int, indice du premier mouvement détecté
    """

    signal = np.asarray(signal, dtype=float)
    N = len(signal)
    duree_s = N / fs

    # ------------------------------------------------------------------
    # Paramètres — dérivés de la durée du signal
    # ------------------------------------------------------------------
    # Fenêtre courte n : environ 5 % de la durée, bornée entre 10 ms et 500 ms
    # Correspond à ≈ 1 période du signal d'arrivée (Table 1 de l'article)
    n_ms  = np.clip(duree_s * 1000 * 0.05, 10, 500)

    # Fenêtre EPS ne : 1.5 × n  (Table 1 de l'article)
    ne_ms = n_ms * 1.5
    n_wait = int(wait_time * fs)  # échantillons à ignorer au début (zone de chauffe)

    # Constante de stabilisation eps (valeur fixe recommandée par les auteurs)
    # Valide car le signal est normalisé dans [-1, 1] avant le calcul
    stabilisation = 0.2

    # Conversion en échantillons
    n  = max(1, int(n_ms  * fs / 1000))
    ne = max(1, int(ne_ms * fs / 1000))

    # ------------------------------------------------------------------
    # Pré-traitement : centrage + normalisation dans [-1, 1]
    # (requis par l'article pour que eps = 0.2 soit cohérent)
    # ------------------------------------------------------------------
    signal_clean = signal - np.mean(signal)
    peak = np.max(np.abs(signal_clean))
    if peak > 0:
        signal_norm = signal_clean / peak
    else:
        return np.zeros(N), np.zeros(N), np.zeros(N), 0

    s2 = signal_norm ** 2

    # ------------------------------------------------------------------
    # ÉTAPE 1 — Calcul de l'énergie-ratio ER(t)   [éqs. (1)-(3)]
    #
    #   E1(t) = somme des s² sur la fenêtre courte  [t-n+1 … t]
    #   E2(t) = somme des s² depuis le début        [0 … t]
    #   ER(t) = E1(t) / (E2(t) + stabilisation)
    # ------------------------------------------------------------------
    e2 = np.cumsum(s2)                                      # fenêtre cumulative

    e1 = np.zeros(N)                                        # fenêtre courte
    e1[n - 1:] = e2[n - 1:] - np.concatenate(([0.0], e2[:N - n]))

    er_raw = e1 / (e2 + stabilisation)

    # ------------------------------------------------------------------
    # ÉTAPE 2 — Lissage EPS  (préserve les transitions abruptes)
    # ------------------------------------------------------------------
    er_filtered = eps(er_raw, window_size=ne)

    # ------------------------------------------------------------------
    # ÉTAPE 3 — Pointé au maximum de la dérivée de l'attribut filtré
    # (on ignore les n premiers échantillons où E1 n'est pas encore plein)
    # ------------------------------------------------------------------
    derivative = np.diff(er_raw, prepend=er_filtered[0])
    derivative[:n] = -np.inf   # zone de chauffe à ignorer

    # Copie de travail : on masque les zones déjà traitées
    deriv_search = derivative.copy()
    deriv_search[:n*2] = -np.inf   # zone de chauffe à ignorer

    # Seuil sur les valeurs positives de la dérivée (hors zone de chauffe)
    valeurs_positives = deriv_search[deriv_search > 0]
    threshold = np.mean(valeurs_positives) * k if len(valeurs_positives) > 0 else np.inf
 
    picks = []
    while True:
        idx_max = int(np.argmax(deriv_search))
 
        # Arrêt si plus aucune valeur exploitable
        if deriv_search[idx_max] < threshold:
            break

        # --- Raffinement : remonter au début de la montée ----------------
        # On cherche en arrière le dernier échantillon où la dérivée était
        # quasi nulle (≤ 10 % du max local), i.e. le vrai onset de la rampe.
        seuil_onset = 0.10 * deriv_search[idx_max]
        idx_onset   = idx_max
        for j in range(idx_max - 1, n*2 - 1, -1):
            if derivative[j] <= seuil_onset:
                idx_onset = j + 1   # premier échantillon au-dessus du seuil
                break
 
        picks.append(idx_onset)
 
        # Masquer la fenêtre de cooldown autour du pic trouvé
        start_mask = idx_onset
        end_mask   = min(N, idx_onset + n_wait)
        deriv_search[start_mask:end_mask] = -np.inf
 
    picks.sort()

    return er_raw, er_filtered, derivative, picks, threshold


# ── Utilisation ────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # ---- Signal synthétique de test --------------------------------------
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
    # ---- Données réelles (décommenter si lecture mseed disponible) ----------

    # #----------MEILLEURE TRACE POUR TESTER-----------------
    trace_brute = lecture_mseed("GUI_20230310_090649.mseed")[0]['data_samples']
    fs    = lecture_mseed("GUI_20230310_090649.mseed")[0]['sample_rate_hz']     
    print(f"Fréquence d'échantillonnage : {fs} Hz")
    t     = np.arange(len(trace_brute)) / fs
    trace = eps(trace_brute, window_size=5)

    
    #---- Trace fourni par Hugo pour des test-----------------
    # data_folder = "../../data_node_1"
    # fs = 100  # sampling rate (Hz)

    # all_data = []
    # for fpath in sorted(glob.glob(data_folder + "/geophone_*.dat")):
    #     data = np.fromfile(fpath, dtype=np.int16)
    #     all_data.append(data)
    # trace_brute = np.array(np.concatenate(all_data), dtype=np.float64)
    # trace = eppf(trace_brute, window_size=81, degree=2)
    # t = np.arange(len(trace)) / fs
    
    # # -------------------------------------------------------------------------

    # ---- Appel MCM -------------------------------------------------------
    er_raw, er_filtered, derivative, picks, threshold = compute_mcm(trace_brute, fs, k=10)

    if picks:
        print(f"{len(picks)} pointé(s) détecté(s)")
        for i, p in enumerate(picks):
            print(f"  Pointé {i+1} : échantillon {p}  ({t[p]:.4f} s)")
    else:

        print("Aucun pointé détecté.")
    # ---- Affichage -------------------------------------------------------
    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
    fig.suptitle("MCM — Sabbione & Velis (2010)", fontsize=13)

    ax0 = axes[0]
    ax0.plot(t, trace_brute , color='grey', lw=0.7, label="Signal brut")
    ax0.plot(t, trace       , color='blue', lw=1.5, label="Signal filtré (EPS)")
    # ax0.axvline(t[onset], color='green', lw=1.5, ls='--', label="Vrai onset")
    if picks:
        for p in picks:
            ax0.axvline(t[p], color='red', lw=1.5, ls='--')
        ax0.axvline(t[picks[0]], color='red', lw=1.5, ls='--', label="MCM picks")
    ax0.set_ylabel("Amplitude")
    ax0.legend(fontsize=8)
    ax0.set_title("Signal sismique")

    ax1 = axes[1]
    ax1.plot(t, threshold * np.ones_like(t), color='black', lw=1.5, ls='--', label=f"Seuil = {threshold:.3f}")
    ax1.plot(t, er_raw,      color='grey',       lw=0.8, label="ER brut")
    ax1.plot(t, er_filtered, color='darkorange',  lw=1.5, label="ER filtré (EPS)")
    # ax1.axvline(t[onset], color='green', lw=1.5, ls='--')
    if picks:
        for p in picks:
            ax1.axvline(t[p], color='red', lw=1.5, ls='--')
        ax1.axvline(t[picks[0]], color='red', lw=1.5, ls='--', label="MCM picks")
    ax1.set_ylabel("Énergie-ratio ER(t)")
    ax1.legend(fontsize=8)
    ax1.set_title("Attribut énergie-ratio (brut et filtré)")

    ax2 = axes[2]
    ax2.plot(t, derivative, color='purple', lw=1.2, label="d(ER filtré)/dt")
    # ax2.axvline(t[onset], color='green', lw=1.5, ls='--', label="Vrai onset")
    if picks:
        for p in picks:
            ax2.axvline(t[p], color='red', lw=1.5, ls='--')
        ax2.axvline(t[picks[0]], color='red', lw=1.5, ls='--', label="MCM pick (max dérivée)")
    ax2.set_ylabel("Dérivée")
    ax2.set_xlabel("Temps (s)")
    ax2.legend(fontsize=8)
    ax2.set_title("Dérivée de l'attribut filtré — le max donne le pointé")

    plt.tight_layout()
    plt.show()
