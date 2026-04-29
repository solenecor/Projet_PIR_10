from ts2vg import NaturalVG
import pylab as P
from time import time
import sys 
import os
import numpy as np
from calculs_matriciels import *
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import *


def clustering_visibility_graph(l_series, nb_seg = 30) :
    """
    Effectue le clustering sur les séries temporelles en utilisant les graphes de visibilité pondérés
    Entrées :
        l_series : array d'array numpy, chaque array correspond à une série temporelle
        nb_seg : entier, nombre de segments à découper pour chaque série
    Sorties :
        G : graphe networkx
    """
    # Découpage en un même nombre de segments :
    segments_tot = []
    for serie in l_series :
        segments_tot.append(decoupe_segments(serie, nb_seg))

    l_vecteurs = [[] for _ in range(nb_seg)]

    # Transfo de chaque segment en weighted visibility graph :
    for serie in segments_tot :
        for idx_seg in range(nb_seg) :
            seg = serie[idx_seg]
            vg = NaturalVG(weighted="abs_slope")  # poids = pente absolue entre les points
            vg.build(seg)
            edges = vg.edges
            n = len(seg)
            # Matrice d'adjacence du graphe :
            adj_matrix = np.zeros((n, n))
            for u,v,w in edges:
                adj_matrix[u, v] = w
                adj_matrix[v, u] = w  # symétrique
            # Calcul du vecteur :
            vect = []
            for u in range (len(adj_matrix)) :
                composante = 0
                for v in range(len(adj_matrix)) :
                    if adj_matrix[u, v] != 0 :
                        composante += 1
                vect.append(composante)
            l_vecteurs[idx_seg].append(vect)


    # Calcul des matrices pour chaque segment :
    matrices = []
    for i in range(len(l_vecteurs)) :
        matrices.append(matrice_segment(l_vecteurs[i]))


    # Calcul de la matrice de distance globale :
    m_distance_globale = matrice_distance_globale(matrices)

    
    # Calcul de la matrice de similarité : 
    m_similarite = matrice_similarite(m_distance_globale)

    # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G 

def clustering_distance_dtw(l_series) :
    """
    Effectue le clustering sur les séries temporelles en utilisant la distance DTW
    Entrées :
        l_series : liste d'array numpy, chaque array correspond à une série temporelle
    Sorties :
        G : graphe networkx
    """
    # Calcul de la matrice de distance globale :
    m_distance_globale = matrice_distance_globale_autres(l_series, distance_dtw)

    # Calcul de la matrice de similarité : 
    m_similarite = matrice_similarite(m_distance_globale)

    # # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G


if __name__ == "__main__" :
    print(os.getcwd())

    data2 = lecture_mseed("event_CALF.mseed")
    data1 = lecture_mseed("event_CREF.mseed")

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

    serie1 = np.array(serie1)
    serie2 = np.array(serie2)

    start_time = time()
    G_visibility = clustering_visibility_graph([serie1, serie2], nb_seg=30)
    print("Graphe de du clustering 1 construit")
    end_time = time()
    print(f"Temps de construction du graphe 1 : {end_time - start_time:.2f} secondes")

    start_time = time()
    G_dtw = clustering_distance_dtw([serie1, serie2])
    print("Graphe de du clustering 2 construit")
    end_time = time()
    print(f"Temps de construction du graphe 2 : {end_time - start_time:.2f} secondes")


    draw_circular(G_visibility, node_color="red")
    draw_circular(G_dtw, node_color="green")
    P.show()
