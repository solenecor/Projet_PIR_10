import numpy as np
from random import randint
import matplotlib.pyplot as plt
from Lecture_data.lecture_mseed import lecture_mseed

def MER(signal, wl, fs):
    '''
    Calcul du MER du signal
    Entrées:
        signal : tableau numpy
        wl : durée de la fenêtre d'energie en ms (int)
        fs : fréquence du signal en Hz (float)
    Sortie:
        res : MER du signal sous forme de tableau numpy
    '''
    # Calcul nb de pts dans une fenêtre (ne)
    Sr = 10**3/fs
    ne = int(wl/Sr)

    b = np.full(ne, np.mean(signal[1 : 2]))
    a = np.full(ne, np.mean(signal[-2 : -1]))
    msignal = np.concatenate((b, signal, a))
    carre = np.square(msignal)
    res = []

    for i in range(1+ne, len(signal)+ne-1):
        num = sum(carre[i : i+ne])
        deno = sum(carre[i-ne : i])
        if deno == 0:
            deno = 10**(-4)
        ratio = num/deno
        mer_i = (np.abs(msignal[i])*ratio)**3
        res.append(mer_i)
    
    res = np.concatenate(([res[0]], res, [res[-1]]))
    return res

def first_detection_MER(mer, seuil):
    t=0
    while mer[t] < seuil:
        t+=1
    return t

def detection_MER(mer, seuil, wait_time):
    detect = []
    for t in range(len(mer)):
        if mer[t] >= seuil:
            if not (detect != [] and t-detect[-1] <= wait_time):
                detect.append(t)
    return detect


if __name__ == "__main__":
    ### Signal data
    trace = lecture_mseed("event.mseed")[0]['data_samples']
    fs = lecture_mseed("event.mseed")[0]['sample_rate_hz']

    wl_ms = 10  # window length

    ### Test
    Mer = MER(trace, wl_ms, fs)
    print(detection_MER(Mer, np.max(Mer)*2/3))

    ### Affichage
    plt.figure()
    plt.subplot(2,1,1)
    plt.plot(trace, color='r')
    plt.subplot(2,1,2)
    plt.plot(Mer, color='b')
    plt.show()