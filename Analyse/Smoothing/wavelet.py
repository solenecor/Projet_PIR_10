import numpy as np
import pywt
import time
import sys
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import lecture_mseed
script_dir = os.path.dirname(os.path.abspath(__file__))
full_in_path = os.path.join(script_dir, "..", "..", "donnees_capteur1.mseed")

# règle "universal" pour lambda
def wavelet_transform(signal, wavelet_type, decomposition_level):

    # Décomposition (db1 = Daubechies d'ordre 1 = Haar)
    coeffs = pywt.wavedec(signal, wavelet=wavelet_type, level=decomposition_level) # liste de tableaux de la forme [cA_N, cD_N, cD_N-1, ..., cD_1] avec cA_i coef d'approx niveau max (basses freq -> laisse intact) et cD_i coef de détail niveau i

    lbda = np.sqrt(2* np.log(len(signal)))

    coeffs_denoised = [coeffs[0]] # on garde l'approximant

    # on seuille pour tous les coefs de détails
    for coef_detail in coeffs[1:]:
        coef_denoised = []
        for c in coef_detail:
            # seuillage doux
            if np.abs(c) >= lbda:
                c_denoised = np.sign(c)* (np.abs(c) - lbda)
            else:
                c_denoised = 0

            coef_denoised.append(c_denoised)

        coeffs_denoised.append(np.array(coef_denoised))
        

    # Reconstruction
    denoised_signal = pywt.waverec(coeffs_denoised, wavelet=wavelet_type)

    return denoised_signal


if __name__ == "__main__":
    trace_file = "../data_node_1_part.mseed"
    data_trace = lecture_mseed(full_in_path)
    raw_trace = data_trace[0]["data_samples"]

    start = time.time()
    for i in range(10):
        wavelet_transform(raw_trace, 'haar', 5)
    print((time.time() - start)/10)

