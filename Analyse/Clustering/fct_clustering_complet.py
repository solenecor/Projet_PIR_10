from ts2vg import NaturalVG
import pylab as P
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



def clustering_visibility_graph(l_series, nb_seg = 30) :
    """
    Effectue le clustering sur les séries temporelles en utilisant les graphes de visibilité pondérés
    Entrées :
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

    # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G, m_similarite 

def clustering_distance_dtw(l_series) :
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

    # # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G, m_similarite 

def clustering_distance_L1(l_series, ) :
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

    # # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G, m_similarite 

def clustering_distance_L2(l_series) :
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

    # # Transfo en graphe : 
    G = transfo_graphe(m_similarite)

    return G, m_similarite 

def lecture_initiale() :
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
    On prend 10 points avant la détection de l'événement
    """

    l_data = [data1_1, data1_2, data2_1, data2_2, data3_1, data3_2]
    dict_data = { "liste_data" : l_data, "tags" : [32.574, 32.61, 34.06, 34.36, 33.60, 33.75], "series" : [], "sr" : [], "longueurs" : []}

    ### Ajout de toutes les séries temporelles dans la liste
    for i in range(len(l_data)) : 
        dict_data["sr"].append(l_data[i][0]["sample_rate_hz"])
        debut = int(dict_data["tags"][i] * dict_data["sr"][-1]) - 10
        serie = np.array(l_data[i][0]["data_samples"])

        # On prend 50 secondes de données à partir du début de l'événement
        serie = serie[debut:debut + int(50 * dict_data["sr"][-1])]
        serie_lisse = eps(serie, window_size=10)
        dict_data["series"].append(serie_lisse)
        dict_data["longueurs"].append(len(serie_lisse))

        print("Série", i, "ajoutée, longueur : ", len(serie_lisse))
    
    ### On met toutes les séries à la même longueur 
    minimum = min(dict_data["longueurs"])
    for i in range(len(dict_data["series"])) :
        if len(dict_data["series"][i]) > minimum :
            dict_data["series"][i] = resample(dict_data["series"][i], minimum)
            dict_data["longueurs"][i] = len(dict_data["series"][i])
            # print("Série", i, "modifiée, nouvelle longueur : ", dict_data["longueurs"][i])
    print("Resample des séries fini")



    return dict_data["series"]

if __name__ == "__main__" :

    series = lecture_initiale()

    start_time = time()
    G_visibility, m_visibility = clustering_visibility_graph(series, nb_seg=30)
    print("Graphe du clustering 1 construit")
    end_time = time()
    print(f"Temps de construction du graphe 1 : {end_time - start_time:.2f} secondes")
   
    start_time = time()
    G_L1, m_L1 = clustering_distance_L1(series)
    print("Graphe du clustering 2 construit")
    end_time = time()
    print(f"Temps de construction du graphe 2 : {end_time - start_time:.2f} secondes")

    start_time = time()
    G_L2, m_L2 = clustering_distance_L2(series)
    print("Graphe du clustering 3 construit")
    end_time = time()
    print(f"Temps de construction du graphe 3 : {end_time - start_time:.2f} secondes")
    
    start_time = time()
    G_dtw, m_dtw = clustering_distance_dtw(series)
    print("Graphe du clustering 4 construit")
    end_time = time()
    print(f"Temps de construction du graphe 4 : {end_time - start_time:.2f} secondes")

    plt.figure(1)
    pos = nx.spring_layout(G_visibility, weight='weight')
    nx.draw_networkx(G_visibility, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_visibility, 'weight').items()}
    nx.draw_networkx_edge_labels(G_visibility, pos, edge_labels=edge_labels)


    plt.figure(2)
    pos = nx.spring_layout(G_L1, weight='weight')
    nx.draw_networkx(G_L1, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_L1, 'weight').items()}
    nx.draw_networkx_edge_labels(G_L1, pos, edge_labels=edge_labels)

    plt.figure(3)
    pos = nx.spring_layout(G_L2, weight='weight')
    nx.draw_networkx(G_L2, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_L2, 'weight').items()}
    nx.draw_networkx_edge_labels(G_L2, pos, edge_labels=edge_labels)


    plt.figure(4)
    pos = nx.spring_layout(G_dtw, weight='weight')
    nx.draw_networkx(G_dtw, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_dtw, 'weight').items()}
    nx.draw_networkx_edge_labels(G_dtw, pos, edge_labels=edge_labels)

    plt.show()


    ### Comparaison de la similarité si on a que 2 séries:
    
    """print(f"Similarité ac visibility graph : {G_visibility.edges[0,1]['weight']}")
    print(f"Similarité ac DTW : {G_dtw.edges[0,1]['weight']}")
    print(f"Similarité ac L1 : {G_L1.edges[0,1]['weight']}")
    print(f"Similarité ac L2 : {G_L2.edges[0,1]['weight']}")"""
