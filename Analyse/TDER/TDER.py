import numpy as np
from random import randint
import matplotlib.pyplot as plt
import glob
from Lecture_data.lecture_mseed import *
import time

def DER(signal, sw, lw, fs):
    ns = int(sw*fs)
    nl = int(lw*fs)

    energy = np.square(signal)
    der = np.zeros(len(signal))

    for t in range(nl+ns, len(signal)-ns):
        # Calculs d'énergies
        E1 = np.mean(energy[t : t+ns-1])
        E2 = np.mean(energy[t-nl+1 : t])
        E3 = np.mean(energy[t-ns-nl+1 : t-ns])
        
        E2 = np.maximum(E2, 1e-6)
        E3 = np.maximum(E3, 1e-6)
        
        # Ratios d'énergie
        ER12 = E1/E2
        ER13 = E1/E3
            
        der[t] = np.log(ER13) - np.log(ER12)

    return der


def TDER(signal, sw, lw, fs):
    '''
    Calcul du TDER du signal
    Entrées:
        signal : tableau numpy
        sw : durée de la courte fenêtre d'énergie en s (int)
        lw : durée de la longue fenêtre d'energie en s (int)
        fs : fréquence du signal en Hz (float)
    Sortie:
        res : MER du signal sous forme de tableau numpy
    '''
    # Calcul nb de pts dans une fenêtre
    ns = int(sw*fs)
    nl = int(lw*fs)

    energy = np.square(signal)

    # Calcul DER
    der = DER(signal, sw, lw, fs)
    
    # Calcul TDER
    tder = []
    tm = np.argmax(der)

    if tm < 2*ns:
        return np.zeros(len(der))

    for i in range(1, len(signal)-1):
        if (i >= tm-2*ns) and (i <= tm):
            a = (der[tm]-der[tm-2*ns])/(2*ns)
            b = der[tm-2*ns]
            tder.append(der[i]-(a*(i-(tm-2*ns))+b))

        else:
            tder.append(0)

    tder = np.concatenate(([tder[0]], tder, [tder[-1]])) # pour avoir le meme nombre de points
    return tder

def detection_DER(der, seuil):
    detect = []
    for t in range(len(der)):
        if der[t] >= seuil:
            if not (detect != [] and t-detect[-1] <= 10):
                detect.append(t)
    return detect

def detection_TDER(tder, seuil, wait_time):
    """
    Détecte uniquement la première perturbation dans le signal
    """
    detect = []
    for t in range(len(tder)):
        if tder[t] >= seuil:
            if not (detect != [] and t-detect[-1] <= wait_time):
                detect.append(t)
    return detect


if __name__=="__main__":
    data_folder = "trace_capteur"
    fs = 100  # sampling rate (Hz)

    # Concatenate data from all file in the data folder
    all_data = []
    for fpath in sorted(glob.glob(data_folder + "/geophone_*.dat")):
        data = np.fromfile(fpath, dtype=np.int16)
        all_data.append(data)
    trace = np.array(np.concatenate(all_data), dtype=np.float64)
    """
    trace = lecture_mseed("event.mseed")[0]['data_samples']
    fs = lecture_mseed("event.mseed")[0]['sample_rate_hz']
    """
    sw = 0.05  # short window length in s
    lw = 0.3 # long window length in s

    ### Test
    deb_der = time.time()
    Der = DER(trace, sw, lw, fs)
    fin_cal_der = time.time()
    seuil_der = np.mean(Der) + 2*np.std(Der)
    det_der = detection_DER(Der, seuil_der)
    fin_det_der = time.time()

    deb_tder = time.time()
    Tder = TDER(trace, sw, lw, fs)
    fin_cal_tder = time.time()
    seuil_tder = np.mean(Tder) + 2*np.std(Tder)
    det_tder = detection_TDER(Tder, seuil_tder)
    fin_det_tder = time.time()

    print(f"DER : {det_der}")
    print(f"TDER : {det_tder}")
    print(f"Temps calcul DER : {fin_cal_der-deb_der}    Temps détection DER : {fin_det_der-deb_der}")
    print(f"Temps calcul TDER : {fin_cal_tder-deb_tder}    Temps détection TDER : {fin_det_tder-deb_tder}")

    ### Affichage
    plt.figure()
    plt.subplot(3,1,1)
    plt.plot(trace, color='r')
    plt.subplot(3,1,2)
    plt.plot(Der, color='g')
    plt.subplot(3,1,3)
    plt.plot(Tder, color='b')
    plt.show()