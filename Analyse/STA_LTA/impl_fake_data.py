import random
import numpy as np


trace = [100]*1500
trace.extend([random.randint(-2048,2048) for i in range(3000)])
sampling_rate = 100 # freq d'échantillonage
time_trace = np.arange(len(trace)) / sampling_rate
sta_duration = 1
lta_duration = 10
threshold = 3

ns = int(sta_duration * sampling_rate)
nl = int(lta_duration * sampling_rate)


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



def detection_STA_LTA():

    i = nl
    sta_list = [-1]* 4500
    lta_list = [-1]* 4500

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

            return detection_index, sta_list, lta_list, trace      

        i += 1

    return -1, sta_list, lta_list, trace