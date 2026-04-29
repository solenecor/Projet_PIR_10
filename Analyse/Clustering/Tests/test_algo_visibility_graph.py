from ts2vg import NaturalVG
import sys 
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Lecture_data.lecture_mseed import *
from Clustering.calculs_matriciels import *

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


# Découpage en un même nombre de segments :
nb_seg = 30 
segments1 = decoupe_segments(serie1, nb_seg)
segments2 = decoupe_segments(serie2, nb_seg)

segments_tot = [segments1, segments2]
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

