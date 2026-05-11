import numpy as np
from scipy.signal import hilbert
import sys
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import lecture_mseed
script_dir = os.path.dirname(os.path.abspath(__file__))
full_in_path = os.path.join(script_dir, "..", "..", "donnees_capteur1.mseed")
from time import time
import matplotlib.pyplot as plt



def multi_window(trace, t, m, n, q, d, p, alpha, env, h2, h3):
    ''' time point t; m, n, and q represent the lengths of the windows in 
    samples,d is the time delay for a DTA window, alpha is the coefficient to
    adjust the height of the first threshold and p is the number of shifted samples
    '''
    
    h1_slice = env[max(0, t-m-p) : max(0, t-p)]
    
    if h1_slice.size == 0:
        # Si la fenêtre est vide (au tout début), on met h1 à une valeur très haute pour éviter les fausses détections
        h1 = 0.0 
    else:
        h1 = np.mean(h1_slice) + alpha * np.std(h1_slice)

    r2 = 1.0
    r3 = 1.0
   

    if np.abs(trace[t]) > h1:

        bta_window = trace[max(0,t-m) : t]
        ata_window = trace[t : min(t+n, len(trace))]
        dta_window = trace[min(t+d, len(trace)) : min(t+d+q, len(trace))]

        if t != 0:
            bta_energy = np.mean(np.abs(bta_window))
        else:
            bta_energy = 0.0

        if t != len(trace):
            ata_energy = np.mean(np.abs(ata_window))
        else:
            ata_energy = 0.0
        
        if t+d < len(trace):
            dta_energy = np.mean(np.abs(dta_window))
        else:
            dta_energy = 0.0

        if bta_energy != 0:
            r2 = ata_energy / bta_energy
            r3 = dta_energy / bta_energy    
        

        if r2 > h2 and r3 > h3:

            is_detected = True

            # on applique le gradient pour améliorer la précision
            idx_start = max(0, t - 3)
            idx_end = min(len(trace), t + 3)
            y_grad = np.abs(trace[idx_start : idx_end])
            x_grad = np.arange(len(y_grad))
            pente = np.polyfit(x_grad, y_grad, 1) # donne eq de droite y = ax + b(ordre 1) sous la forme [a, b]
            if pente[0] != 0:
                t = t - np.abs(trace[t])/pente[0]

        else:

            is_detected = False

    else:

        is_detected = False

    return is_detected, t, r2, r3, h1


def detection_multi_window(trace, m, n, q, d, p, alpha, average_snr, sample_rate, wait_time):
    env = np.abs(hilbert(trace))

    i = 0
    h1 = [-10]*len(trace)
    h2 = [0.75*average_snr]*len(trace)
    h3 = [0.75*average_snr]*len(trace)

    r2 = [-10]*len(trace)
    r3 = [-10]*len(trace)

    detection_indexes = []

    while i < len(trace):
        # on fait le ratio point par point
        is_detected, detection_index, r2[i], r3[i], h1[i]= multi_window(trace, i, m, n, q, d, p, alpha, env, h2[i], h3[i])
        
        if is_detected:
            # quand on détecte un dépassement du seuil
            if len(detection_indexes) == 0 or detection_index > detection_indexes[-1] + sample_rate * wait_time: # on attend 10s pour qu'il ne s'agisse pas du même évènement (ou alors s'il y a pas déjà d'autre détection)
                detection_indexes.append(detection_index)
        
        i += 1 
    return detection_indexes, r2, r3, h1, h2, h3



def plot_windows(trace, t, m, n, q, d, p):
    """
    Affiche la trace avec les zones correspondant aux 3 fenêtres de détection
    """
    t = int(t)
    fig = plt.figure(figsize=(14, 6))
    ax = fig.add_subplot(111)
    
    # Fenêtre de vue large pour voir la trace
    view_margin = int(2.0 * max(m, n, q+d))
    zoom_range = np.arange(max(0, t-view_margin), min(len(trace), t+view_margin))
    
    # --- Tracé du Signal ---
    plt.plot(zoom_range, trace[zoom_range], color='#A52A2A', linewidth=2, label='Signal')
    
    # --- Calcul des hauteurs ---
    max_amp = np.max(np.abs(trace[zoom_range]))
    h_step = max_amp * 0.25
    
    def draw_box(start, end, height, color, label):
        if start >= end: return
        plt.plot([start, start, end, end], [0, height, height, 0], 
                 color=color, linewidth=3, label=label)

    # --- Fenêtres (Légende simple sans paramètres) ---
    draw_box(max(0, t-m), t, max_amp + h_step, '#1E90FF', 'BTA')
    draw_box(t, min(t+n, len(trace)), max_amp + 2*h_step, '#3CB371', 'ATA')
    draw_box(min(t+d, len(trace)), min(t+d+q, len(trace)), max_amp + 3*h_step, '#FF4500', 'DTA')

    # --- Annotation Test Point ---
    plt.annotate('test point $i$', xy=(t, 0), xytext=(t, max_amp + 4.5*h_step),
                 arrowprops=dict(facecolor='black', width=1, headwidth=7),
                 ha='center', fontsize=12, fontweight='bold')

    # --- Ajustement des axes et suppression des graduations ---
    plt.xticks([])
    plt.yticks([])
    
    # Retrait des bordures pour l'aspect schéma
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Ajout d'une ligne d'axe X discrète
    plt.axhline(0, color='black', linewidth=0.8, alpha=0.5)

    # Légende simple
    plt.legend(loc='upper right', frameon=True, fontsize=11)
    
    # AJUSTEMENT CRUCIAL : On augmente la marge basse (0.8 au lieu de 0.3) 
    # pour que les pics négatifs du signal ne soient pas coupés.
    plt.ylim(-max_amp * 1.2, max_amp + 6*h_step)
    plt.xlim(zoom_range[0], zoom_range[-1])
    
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    trace_file = "../data_node_1_part.mseed"
    data_trace = lecture_mseed(full_in_path)
    sample_rate = data_trace[0]["sample_rate_hz"]
    raw_trace = data_trace[0]["data_samples"]
    ns = int(0.1 * sample_rate)
    nl = int(1 * sample_rate)
    start = time()
    # for i in range(10):
    #     detection_multi_window(raw_trace, 30, 5, 5, 2, 2, 3.5, 2.5, sample_rate, 5)
    # print((time()-start)/10)
    m, n, q, d, p = 30, 5, 5, 2, 2
    alpha, snr, wait = 3.5, 2.5, 5
    
    # Exécution de la détection
    detections, r2, r3, h1, h2, h3 = detection_multi_window(
        raw_trace, m, n, q, d, p, alpha, snr, sample_rate, wait
    )
    target_t = int(detections[0])
    plot_windows(raw_trace, target_t, m, n, q, d, p)