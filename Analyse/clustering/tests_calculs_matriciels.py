from calculs_matriciels import *

### Imports :
import numpy as np
import random as rd
from networkx import * 
import pylab as P
import matplotlib.pyplot as plt


### Tests :
# Génération des tests :

# Segment 1 :
v1 = np.array([])
v2 = np.array([])
v3 = np.array([])
v4 = np.array([])
# Segment 2 :
v5 = np.array([])
v6 = np.array([])
v7 = np.array([])
v8 = np.array([])

for i in range(10) :
    v1 = np.append(v1, rd.randint(0, 500))
    v2 = np.append(v2, rd.randint(0, 500))
    v3 = np.append(v3, rd.randint(0, 500))
    v4 = np.append(v4, rd.randint(0, 500))
    v5 = np.append(v5, rd.randint(0, 500))
    v6 = np.append(v6, rd.randint(0, 500))
    v7 = np.append(v7, rd.randint(0, 500))
    v8 = np.append(v8, rd.randint(0, 500))

# Affichage des tests :

# Vecteurs :
print("Vecteurs aléatoires 1 à 4 : \n")
print("v1 : ", v1)
print("v2 : ", v2)
print("v3 : ", v3)
print("v4 : ", v4, "\n")

# Distance euclidienne entre v1 et v2 :
print("Distance euclidienne entre v1 et v2 :", d_euclidienne(v1, v2), "\n \n")

# Matrice de distance pour les 2 segments :
mat_1 = matrice_segment([v1, v2, v3, v4])
mat_2 = matrice_segment([v5, v6, v7, v8])

print("Matrice de distance pour le segment 2 : \n", mat_2, "\n \n")

l_matrices = [mat_1, mat_2] 

# Calcul de la matrice de distance globale : 
m_d_globale = matrice_distance_globale(l_matrices)
print("Matrice de distance globale : \n", m_d_globale)

# Calcul de la matrice de similarité :
m_similarite = matrice_similarite(m_d_globale)
print("Matrice de similarite : \n", m_similarite)

# Création d'un graphe à partir de la matrice : 
G = transfo_graphe(m_similarite)

# Community detection avec la méthode Louvain :
communities = community.louvain_communities(G,resolution=1.6, seed=2)
print(communities)


# Affichage du graphe :
plt.figure()
pos = fruchterman_reingold_layout(G)
draw_networkx_nodes(G, pos, 
                       node_color = 'blue', 
                       node_size = 500)
draw_networkx_labels(G, pos)
draw_networkx_edges(G, pos, arrows=False)
labels = get_edge_attributes(G,'weight')
draw_networkx_edge_labels(G,pos,edge_labels=labels)
plt.show()






