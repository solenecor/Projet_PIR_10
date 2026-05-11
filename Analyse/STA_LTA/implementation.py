import numpy as np
import sys
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import lecture_mseed
script_dir = os.path.dirname(os.path.abspath(__file__))
full_in_path = os.path.join(script_dir, "..", "..", "donnees_capteur1.mseed")
from time import time

def STA_LTA(trace, i, ns, nl, threshold):

    sta_window = trace[max(0,i-ns) : i]
    lta_window = trace[max(0, i-nl) : i]

    sta_energy = 0.0
    lta_energy = 0.0

    if i != 0 :
        sta_energy = np.mean(np.square(sta_window))

        lta_energy = np.mean(np.square(lta_window))

    if lta_energy != 0:
        ratio = sta_energy/lta_energy
    else :
        ratio = 1.0

    if ratio > threshold:
        is_detected = True
    else:
        is_detected = False
    return is_detected, i, ratio

    
def detection_STA_LTA(trace, ns, nl, threshold, sample_rate, wait_time):
    start = time()
    i = 0
    ratio = [-10] * len(trace)
    detection_indexes = []
    while i < len(trace):
        # on fait le ratio point par point
        is_detected, detection_index, ratio[i] = STA_LTA(trace, i, ns, nl, threshold)
        

        if is_detected:
            # quand on détecte un dépassement du seuil
            if len(detection_indexes) == 0 or detection_index > detection_indexes[-1] + sample_rate * wait_time: # on attend 10s pour qu'il ne s'agisse pas du même évènement (ou alors s'il y a pas déjà d'autre détection)
                detection_indexes.append(detection_index)
        
        i += 1 
    print(time()-start)
    return detection_indexes, ratio

if __name__ == "__main__":
    trace_file = "../data_node_1_part.mseed"
    data_trace = lecture_mseed(full_in_path)
    sample_rate = data_trace[0]["sample_rate_hz"]
    raw_trace = data_trace[0]["data_samples"]
    ns = int(0.1 * sample_rate)
    nl = int(1 * sample_rate)
    for i in range(10):
        detection_STA_LTA(raw_trace, ns, nl, 3, sample_rate, 5)
