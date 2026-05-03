import numpy as np
from scipy.signal import hilbert


def multi_window(trace, t, m, n, q, d, p, alpha, env, h2, h3):
    ''' time point t; m, n, and q represent the lengths of the windows in 
    samples,d is the time delay for a DTA window, alpha is the coefficient to
    adjust the height of the first threshold and p is the number of shifted samples
    '''
    bta_window = trace[max(0,t-m) : t]
    ata_window = trace[t : min(t+n, len(trace))]
    dta_window = trace[min(t+d, len(trace)) : min(t+d+q, len(trace))]
    
    h1_slice = env[max(0, t-m-p) : max(0, t-p)]
    

    if h1_slice.size == 0:
        # Si la fenêtre est vide (au tout début), on met h1 à une valeur très haute pour éviter les fausses détections
        h1 = 0.0 
    else:
        h1 = np.mean(h1_slice) + alpha * np.std(h1_slice)

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
    else :
        r2 = 1.0
        r3 = 1.0

    if np.abs(trace[t]) > h1:

        if r2 > h2 and r3 > h3:

            is_detected = True

            # on applique le gradient pour améliorer la précision
            idx_start = max(0, t - 5)
            idx_end = min(len(trace), t + 5)
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


def detection_multi_window(trace, m, n, q, d, p, alpha, average_snr, sample_rate):

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
            if len(detection_indexes) == 0 or detection_index > detection_indexes[-1] + sample_rate * 10: # on attend 10s pour qu'il ne s'agisse pas du même évènement (ou alors s'il y a pas déjà d'autre détection)
                detection_indexes.append(detection_index)
        
        i += 1 
    return detection_indexes, r2, r3, h1, h2, h3
