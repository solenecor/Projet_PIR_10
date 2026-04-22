### Imports :
import numpy as np
import numpydoc as npdoc
import random as rd
from networkx import *

### Fonctions de calculs pour l'article principal : 

# Distance euclidienne entre deux vecteurs de même dimension :
def d_euclidienne(v1, v2):
    """
    Calcul de la distance euclidienne entre deux vecteurs v1 et v2.
    Entrées : 
        v1, v2 : listes d'entiers
    Sorties : 
        d : float numpy
    """
    return np.sqrt(np.sum((v1 - v2)**2))

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

# Calcul de la matrice globale :
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

# Calcul de la matrice de similarité :
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






    