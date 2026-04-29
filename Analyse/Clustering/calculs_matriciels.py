### Imports :
import numpy as np
from networkx import *
import sys 
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Analyse.calculs_distance import *

### Fonctions de calculs matriciels pour l'algo avec les weighted visibility graphs : 
def decoupe_segments(serie, n_segments) :
    """
    Découpe une série en plusieurs segments, et renvoie la liste des segments
    Entrées :
        serie : liste de listes d'entiers
        n_segments : entier (nombre de segments)
    Sorties :
        segments : liste de listes de listes d'entiers
    """
    longueur = len(serie)
    taille_segment = longueur // n_segments
    segments = []
    for i in range(n_segments) :
        debut = i * taille_segment
        if i < n_segments - 1 :
            fin = debut + taille_segment
        else :
            fin = longueur
        segments.append(serie[debut:fin])

    return segments

# Calcul de la matrice de distance pour un segment :
def matrice_segment(vecteurs) :
    """
    Calcul la matrice de distance pour un segment donné
    Entrées :
        vecteurs : liste de listes d'entiers (toutes les sous-listes doivent avoir la même longueur)
    Sorties :
        mat : liste de liste de floats
    """
    mat = np.zeros((len(vecteurs), len(vecteurs)))
    for i in range(len(vecteurs)) :
        for j in range(0, i) :
            mat[i, j] = d_euclidienne(vecteurs[i], vecteurs[j])
            mat[j, i] = mat[i, j]
    return mat  

# Calcul de la matrice globale pour l'article principal :
def matrice_distance_globale(matrices) :
    """
    Calcul de la matrice de distance globale normalisée, en faisant la moyenne de toutes les matrices
    Entrées : 
        matrices : array de array de array numpy (liste de matrices)
    Sorties :
        m_d : array de array numpy (matrice)
    """       
    # Calcul de la matrice de distance globale :
    m_d = np.zeros((len(matrices[0]), len(matrices[0])))
    for i in range(len(matrices[0])) :
        for j in range(len(matrices[0])) :
            m_d[i, j] = np.mean([matrices[k][i][j] for k in range(len(matrices))])
    
    # Normalisation de la matrice :
    norme = np.linalg.norm(m_d)
    m_d = m_d / norme

    return m_d



### Fonction de la matrice globale pour les autres types de distance : 
def matrice_distance_globale_autres(series, f_distance) :
    """
    Calcule la matrice de distance globale 
    Entrées : 
        series : array de array numpy (liste de séries temporelles)
        f_distance : fonction de distance à appliquer, qui prend en entrée deux séries temporelles et retourne un float
    Sorties :
        m_d : array de array numpy (matrice)
    """
    m_d = np.zeros((len(series), len(series)))
    for i in range(len(series)):
        for j in range(len(series)):
            if i != j:
                m_d[i, j] = f_distance(series[i], series[j])
    
    # Normalisation de la matrice :
    norme = np.linalg.norm(m_d)
    m_d = m_d / norme

    return m_d


### Calcul de la matrice de similarité :
def matrice_similarite(m_distance) :
    """
    Calcul de la matrice de similarité à partir de la matrice de distance globale
    Entrées : 
        m_distance : array de array numpy (matrice)
    Sorties :
        m_s : array de array numpy (matrice)
    """       
    m_s = np.zeros((len(m_distance), len(m_distance)))
    for i in range(len(m_distance)) :
        for j in range(len(m_distance)) :
            if (i == j) :
                m_s[i, j] = 1
            else :
                m_s[i, j] = 1 - m_distance[i, j]
    
    return m_s



### Transformation de la matrice de similarité en graphe :
def transfo_graphe(m_similarite) :
    """
    Calcul le graphe associé à la matrice de similarité
    Entrées : 
        m_similarité : array de array numpy
    Sortie :
        G : graphe networkx
    """
    G = Graph()

    # Ajout des sommets :
    for i in range(len(m_similarite)) :
        G.add_node(i)

    # Ajout des arrêtes :
    for i in range(len(m_similarite)) :
        for j in range(i) :
            if i != j :
                G.add_edges_from([(i,j, {'weight': float(m_similarite[i,j]) })])
    
    return G

