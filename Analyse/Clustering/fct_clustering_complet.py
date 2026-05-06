from ts2vg import NaturalVG
from time import time
import sys 
import os
import numpy as np
from scipy.signal import resample
from calculs_matriciels import *
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from Smoothing.eps import eps
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import *


def affiche_graphe(G):
    """
    Affiche le graphe pondéré G avec le poids des arrêtes arrondi au centième.
    Entrées : 
        G : graphe pondéré networkx
    Sorties: 
        None
    """
    plt.figure()
    pos = nx.spring_layout(G, weight='weight')
    nx.draw_networkx(G, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G, 'weight').items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.show()

def egalise_longueur_serie(dict_data) : 
    """
    Resample les séries du dictionnaire dict_data pour que toutes les séries aient le même nombres de points
    Entrées : 
        dict_data : dictionnaire python, doit contenir une clé "series" et une clé "longueurs" pointant vers des listes
    Sorties : 
        None
    """
    minimum = min(dict_data["longueurs"])
    for i in range(len(dict_data["series"])) :
        if len(dict_data["series"][i]) > minimum :
            dict_data["series"][i] = resample(dict_data["series"][i], minimum)
            dict_data["longueurs"][i] = len(dict_data["series"][i])
            # print("Série", i, "modifiée, nouvelle longueur : ", dict_data["longueurs"][i])
    #print("Resample des séries fini")

def normaliseur(s) :
    """
    Normalise la série s entre -1 et 1, en divisant pas la valeur maximale (en absolu)
    Entrées :
        s : array numpy de float
    Sortie :
        res : array numpy de float, compris entre -1 et 1
    """
    if s is not None :
        val_max = np.max(np.absolute(s))
        if (val_max == 0) or (len(s) == 0) :
            res = s 
        else :
            res = s/val_max
    else : 
        res = None
    return res

def lecture_initiale() :
    ### 6 fichiers, correspond à 3 événements captés par 2 capteurs GUI et RES
    data1_1 = lecture_mseed("GUI_20230103_090203.mseed")
    data1_2 = lecture_mseed("RES_20230103_090203.mseed")
    data2_1 = lecture_mseed("GUI_20230127_090749.mseed")
    data2_2 = lecture_mseed("RES_20230127_090749.mseed")
    data3_1 = lecture_mseed("GUI_20230310_090649.mseed")
    data3_2 = lecture_mseed("RES_20230310_090649.mseed")

    """ 
    tag manuel :
    - GUI_20230103_090203 : début de l'event à (32,574; -21)
    - RES_20230103_090203 : début de l'event à (32,61; 209)
    - GUI_20230127_090749 : (34,06 ; -8)
    - RES_20230127_090749 : (34,36 ; 0)
    - GUI_20230310_090649 : (33,60 ; -28)
    - RES_20230310_090649 : (33,75 ; -2)
    On prend 10 points avant la détection de l'événement, et l'équivalent de 50sec après
    """

    l_data = [data1_1, data1_2, data2_1, data2_2, data3_1, data3_2]
    dict_data = { "liste_data" : l_data, "tags" : [32.574, 32.61, 34.06, 34.36, 33.60, 33.75], "series" : [], "sr" : [], "longueurs" : []}

    ### Ajout de toutes les séries temporelles dans la liste
    for i in range(len(l_data)) : 
        dict_data["sr"].append(l_data[i][0]["sample_rate_hz"])

        # On prend 50 secondes de données à partir du début de l'événement
        debut = int(dict_data["tags"][i] * dict_data["sr"][-1]) - 10
        serie = np.array(l_data[i][0]["data_samples"])
        serie = serie[debut:debut + int(50 * dict_data["sr"][-1])]

        # On enlève le bruit de la série :
        serie_lisse = eps(serie, window_size=10)

        # On normalise la série entre -1 et 1 :
        serie_norme = normaliseur(serie_lisse)

        dict_data["series"].append(serie_norme)
        dict_data["longueurs"].append(len(serie_norme))

        print("Série", i, "ajoutée, longueur : ", len(serie_norme))
    
    ### On met toutes les séries à la même longueur 
    egalise_longueur_serie(dict_data)

    return dict_data["series"]

def clustering_visibility_graph(k, l_series, nb_seg = 30) :
    """
    Effectue le clustering sur les séries temporelles en utilisant les graphes de visibilité pondérés
    Entrées :
        k : entier
        l_series : array d'array numpy, chaque array correspond à une série temporelle
        nb_seg : entier, nombre de segments à découper pour chaque série
    Sorties :
        G : graphe networkx
        m_similarite : matrice numpy (array de array de float)
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

    # Passage par k-NN :
    m_s_knn = knn_graph(m_similarite, k)

    # Transfo en graphe : 
    G = transfo_graphe(m_s_knn)

    return G, m_s_knn

def clustering_distance_dtw(l_series, k) :
    """
    Effectue le clustering sur les séries temporelles en utilisant la distance DTW
    Entrées :
        l_series : liste d'array numpy, chaque array correspond à une série temporelle
    Sorties :
        G : graphe networkx
        m_similarite : matrice numpy (array de array de float)
    """
    # Calcul de la matrice de distance globale :
    m_distance_globale = matrice_distance_globale_autres(l_series, distance_dtw)

    # Calcul de la matrice de similarité : 
    m_similarite = matrice_similarite(m_distance_globale)

    # Passage par k-NN :
    m_s_knn = knn_graph(m_similarite, k)

    # Transfo en graphe : 
    G = transfo_graphe(m_s_knn)

    return G, m_s_knn

def clustering_distance_L1(l_series, k) :
    """
    Effectue le clustering sur les séries temporelles en utilisant la norme L1
    Entrées :
        l_series : liste d'array numpy, chaque array correspond à une série temporelle
    Sorties :
        G : graphe networkx
        m_similarite : matrice numpy (array de array de float)
    """
    # Calcul de la matrice de distance globale :
    m_distance_globale = matrice_distance_globale_autres(l_series, distance_L1)

    # Calcul de la matrice de similarité : 
    m_similarite = matrice_similarite(m_distance_globale)

    # Passage par k-NN :
    m_s_knn = knn_graph(m_similarite, k)

    # Transfo en graphe : 
    G = transfo_graphe(m_s_knn)

    return G, m_s_knn

def clustering_distance_L2(l_series, k) :
    """
    Effectue le clustering sur les séries temporelles en utilisant la norme L2
    Entrées :
        l_series : liste d'array numpy, chaque array correspond à une série temporelle
    Sorties :
        G : graphe networkx
        m_similarite : matrice numpy (array de array de float)
    """
    # Calcul de la matrice de distance globale :
    m_distance_globale = matrice_distance_globale_autres(l_series, distance_L2)

    # Calcul de la matrice de similarité : 
    m_similarite = matrice_similarite(m_distance_globale)

    # Passage par k-NN :
    m_s_knn = knn_graph(m_similarite, k)

    # Transfo en graphe : 
    G = transfo_graphe(m_s_knn)

    return G, m_s_knn

