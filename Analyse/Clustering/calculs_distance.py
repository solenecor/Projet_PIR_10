### Les différents calculs de distance entre séries temporelles :
"""
1) Norme L1 : d(x,y) = sum(|x_i - y_i|)
2) Norme L2 : d(x,y) = sqrt(sum((x_i - y_i)^2))
3) FeatTS : on sélectionne les données statistiques à garder avec la librairie tsfresh, puis pour chaque couple de série on la valeur absolue de la différence pour chaque donnée statistique.
4) Dynamic Time Warping (DTW) : librairie dtw-python, compatible avec numpy
5) Weighted Visibility Graph : on construit un graphe de visibilité pondéré à partir du segment de la série temporelle, puis on construit un vecteur de centralité et on calcule les distances euclidiennes
"""

import numpy as np
from dtw import dtw


def d_euclidienne(v1, v2):
    """
    Calcul de la distance euclidienne entre deux vecteurs v1 et v2, avec les vecteurs sont forme d'objets python.
    Entrées : 
        v1, v2 : listes d'entiers
    Sorties : 
        d : float numpy
    """
    d = 0
    for i in range(len(v1)) :
        d += (v1[i] - v2[i])**2
    d = np.sqrt(d)
    return d
    
def distance_L1(u, v): 
    """
    Calcule la distance L1 entre les deux séries temporelles u et v, points à points, il faut qu'elles aient la même longueur.
    Entrées :
        u : série temporelle, un array numpy     
        v : série temporelle, un array numpy
    Sortie :
        d : float numpy
    """
    d = sum(np.abs(u - v))
    return d

def distance_L2(u, v): 
    """
    Calcule la distance L2 entre les deux séries temporelles u et v, points à points, il faut qu'elles aient la même longueur.
    Entrées :
        u : série temporelle, un array numpy     
        v : série temporelle, un array numpy
    Sortie :
        d : float numpy
    """
    d = np.sqrt(sum((u - v)**2))
    return d

def distance_dtw(u, v) :
    """
    Calcule la distance DTW entre les deux séries temporelles u et v, compatible avec des séries de longueurs différentes.
    Entrées :
        u : série temporelle, un array numpy     
        v : série temporelle, un array numpy    
    Sortie :
        d : float
    """
    alignment = dtw(u, v, keep_internals=True)
    return alignment.distance
