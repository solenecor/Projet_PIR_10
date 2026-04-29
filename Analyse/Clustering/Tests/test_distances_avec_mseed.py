from dtw import dtw
import sys 
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import *
from Clustering.calculs_distance import *


### Récupération des données :
data2 = lecture_mseed("event2.mseed")
data1 = lecture_mseed("event1.mseed")

serie1 = data1[0]["data_samples"]
serie2 = data2[0]["data_samples"]

print("Longueur série 1 :", len(serie1))
print("Longueur série 2 :", len(serie2))

### Si les séries n'ont pas la même longueur, on tronque la plus grande pour faire les tests : 
if len(serie1) > len(serie2):
    serie1 = serie1[:len(serie2)]
    print(f"Série 1 tronquée pour correspondre à la longueur de série 2, nouvelle taille : {len(serie1)}")
elif len(serie2) > len(serie1):
    serie2 = serie2[:len(serie1)]
    print(f"Série 2 tronquée pour correspondre à la longueur de série 1, nouvelle taille : {len(serie2)}")

### Tests des calculs de distance :
print(f"Distance L1 entre les deux séries : {distance_L1(serie1, serie2)}")
print(f"Distance L2 entre les deux séries : {distance_L2(serie1, serie2)}")

### Test du dynamic time warping :
# Calcul du DTW
alignment = dtw(serie1, serie2, keep_internals=True)

# Distance DTW
print(f"Distance brute avec DTW : {alignment.distance}")       
print(f"Distance normalisée par la longueur du chemin avec DTW : {alignment.normalizedDistance}") 

