import numpy as np
import sys 
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Clustering.calculs_distance import *

# Définition des vecteurs de test :
u = np.array([1, 2, 3, 4, 5])
v = np.array([2, 3, 4, 5, 6])

# Test de la distance L1 :
d_L1 = distance_L1(u, v)
verif_L1 = 5
print(f"Vérification de la distance L1 : {d_L1 == verif_L1}")

# Test de la distance L2 :
d_L2 = distance_L2(u, v)
verif_L2 = np.sqrt(sum((u - v)**2))
print(f"Vérification de la distance L2 : {d_L2 == verif_L2}")

