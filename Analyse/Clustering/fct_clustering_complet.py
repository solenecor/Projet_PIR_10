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


def clustering_visibility_graph(l_series, nb_seg = 30, sigma = 1) :
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
    m_similarite = matrice_similarite(m_distance_globale, sigma)

    # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G 

def clustering_distance_dtw(l_series, sigma) :
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
    m_similarite = matrice_similarite(m_distance_globale, sigma)

    # # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G

def clustering_distance_L1(l_series, sigma) :
    """
    Effectue le clustering sur les séries temporelles en utilisant la norme L1
    Entrées :
        l_series : liste d'array numpy, chaque array correspond à une série temporelle
    Sorties :
        G : graphe networkx
    """
    # Calcul de la matrice de distance globale :
    m_distance_globale = matrice_distance_globale_autres(l_series, distance_L1)

    # Calcul de la matrice de similarité : 
    m_similarite = matrice_similarite(m_distance_globale, sigma)

    # # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G

def clustering_distance_L2(l_series, sigma) :
    """
    Effectue le clustering sur les séries temporelles en utilisant la norme L2
    Entrées :
        l_series : liste d'array numpy, chaque array correspond à une série temporelle
    Sorties :
        G : graphe networkx
    """
    # Calcul de la matrice de distance globale :
    m_distance_globale = matrice_distance_globale_autres(l_series, distance_L2)

    # Calcul de la matrice de similarité : 
    m_similarite = matrice_similarite(m_distance_globale, sigma)

    # # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G

def lecture_initiale() :
    data2 = lecture_mseed("GUI_20230103_090203.mseed")
    data1 = lecture_mseed("RES_20230103_090203.mseed")


    serie1 = data1[0]["data_samples"]
    serie2 = data2[0]["data_samples"]


    print("Longueur série 1 :", len(serie1))
    print("Longueur série 2 :", len(serie2))

    sr1 = data1[0]["sample_rate_hz"]
    sr2 = data2[0]["sample_rate_hz"]

    """ 
    tag manuel :
    - GUI_20230103_090203.mseed : début de l'event à (32,574; -21)
    - RES_20230103_090203.mseed : début de l'event à (32,61; 209)
    On prend 10 points avant la détection de l'événement
    """
    debut1 = int(32.574 * sr1) - 10
    debut2 = int(32.61 * sr2) - 10

    serie1 = np.array(serie1)
    serie2 = np.array(serie2)

    serie1 = serie1[debut1:]
    serie2 = serie2[debut2:]

    if len(serie1) > len(serie2) :
        idx = np.linspace(0, len(serie1) -1, len(serie2))
        serie1 = serie1[idx.astype(int)]
    elif len(serie2) > len(serie1) :
        idx = np.linspace(0, len(serie2) -1, len(serie1))
        serie2 = serie2[idx.astype(int)]

    print(len(serie1))
    print(len(serie2))

    return serie1, serie2

if __name__ == "__main__" :

    serie1, serie2 = lecture_initiale()

    ### Ici les valeurs de sigma sont un peu arbitraires, elles sont du même ordre de grandeur que les distances, plus tard il faudra que sigma = moyenne(distance=)

    start_time = time()
    G_visibility = clustering_visibility_graph([serie1, serie2], nb_seg=30, sigma=100)
    print("Graphe du clustering 1 construit")
    end_time = time()
    print(f"Temps de construction du graphe 1 : {end_time - start_time:.2f} secondes")
   
    start_time = time()
    G_L1 = clustering_distance_L1([serie1, serie2], sigma=3000000)
    print("Graphe du clustering 2 construit")
    end_time = time()
    print(f"Temps de construction du graphe 2 : {end_time - start_time:.2f} secondes")

    start_time = time()
    G_L2 = clustering_distance_L2([serie1, serie2], sigma=10000)
    print("Graphe du clustering 3 construit")
    end_time = time()
    print(f"Temps de construction du graphe 3 : {end_time - start_time:.2f} secondes")
    
    start_time = time()
    G_dtw = clustering_distance_dtw([serie1, serie2], sigma=3000000)
    print("Graphe du clustering 4 construit")
    end_time = time()
    print(f"Temps de construction du graphe 4 : {end_time - start_time:.2f} secondes")


    ### Comparaison de la similarité :
    print(f"Similarité ac visibility graph : {G_visibility.edges[0,1]['weight']}")
    print(f"Similarité ac DTW : {G_dtw.edges[0,1]['weight']}")
    print(f"Similarité ac L1 : {G_L1.edges[0,1]['weight']}")
    print(f"Similarité ac L2 : {G_L2.edges[0,1]['weight']}")


    
    