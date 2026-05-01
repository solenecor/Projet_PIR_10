import numpy as np

def STA_LTA(trace, i, ns, nl, threshold):

    sta_window = trace[max(0,i-ns) : i]
    sta_energy = np.mean(np.square(sta_window))

    lta_window = trace[max(0, i-nl) : i]
    lta_energy = np.mean(np.square(lta_window))

    if lta_energy != 0:
        ratio = sta_energy/lta_energy
    else :
        ratio = 1

    if ratio > threshold:
        is_detected = True
    else:
        is_detected = False
    return is_detected, i, ratio

    
def detection_STA_LTA(trace, ns, nl, threshold, sample_rate):
    i = 0
    ratio = [-10] * len(trace)
    detection_indexes = []
    while i < len(trace):
        # on fait le ratio point par point
        is_detected, detection_index, ratio[i] = STA_LTA(trace, i, ns, nl, threshold)
        

        if is_detected:
            # quand on détecte un dépassement du seuil
            if len(detection_indexes) == 0 or detection_index > detection_indexes[-1] + sample_rate * 10: # on attend 10s pour qu'il ne s'agisse pas du même évènement (ou alors s'il y a pas déjà d'autre détection)
                detection_indexes.append(detection_index)
        
        i += 1 
    return detection_indexes, ratio
