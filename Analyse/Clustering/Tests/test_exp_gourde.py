import sys, os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from Lecture_data.decoupage_donnees_gourde import *
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from fct_clustering_complet import clustering_distance_dtw, clustering_distance_L1, clustering_distance_L2, clustering_visibility_graph, lecture_initiale, egalise_longueur_serie



input_file = "donnees_capteur1.mseed"
l_events, fs = decoupe_data_gourde(input_file)
for e in l_events :
        # Affichage avec matplotlib
        t= arange(len(e)) / fs
        plt.plot(t,e)
        plt.show()
