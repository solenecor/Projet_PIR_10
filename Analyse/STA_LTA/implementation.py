import numpy as np

def STA_LTA(trace, i, ns, nl, threshold):

    sta_window = trace[i-ns : i]
    sta_energy = np.mean(np.square(sta_window))

    lta_window = trace[i-nl : i]
    lta_energy = np.mean(np.square(lta_window))

    if lta_energy != 0:
        ratio = sta_energy/lta_energy
    else :
        ratio = 0

    if ratio > threshold:
        is_detected = True
    else:
        is_detected = False
    return is_detected, i

    
def detection_STA_LTA(trace, ns, nl, threshold):
    i = nl
    sta_list = [-1]* len(trace)
    lta_list = [-1]* len(trace)
    while i < len(trace):
        # on fait le ratio point par point
        is_detected, detection_index = STA_LTA(trace, i, ns, nl, threshold)
        
        if is_detected:
            # quand on détecte un dépassement du seuil
            for k in range(len(trace)):
                if detection_index >= k and k >= detection_index - ns:
                    sta_list[k] = 17
                else:
                    sta_list[k] = 0

            for k in range(len(trace)):
                if detection_index >= k and k >= detection_index - nl:
                    lta_list[k] = 16
                else:
                    lta_list[k] = 0

            return detection_index, sta_list, lta_list
        
        i += 1 
    return -1, sta_list, lta_list
