# Fichiers liés au clustering

## Dépendances : 
ts2vg
pylab
numpy
networkx
dtw

## Différentes pipelines suivant la méthode :

##### Pipeline pour le calcul de distance avec le visibility graph : 
Chaque série est découpé en segment
Chaque segment est transformé en weighted visibility graph
Chaque weighted visibility graph est transformé en vecteur
Pour chaque segment, on calcule la matrice de distance avec toutes les séries
On calcule la matrice de distance globale en faisant la moyenne de toutes les autres

##### Pipeline pour les autres calculs de distance :
On calcule la matrice de distance globale en utilisant la fonction de calcul de distance voulue

##### Pour la similarité et les graphes :
Une fois qu'on a la matrice de distance globale (soit avec visibility graph soit avec les autres méthodes) on la normalise avec la méthode min/max
On calcule la matrice de similarité avec : S = 1 - D 
On calcule le graphe adjacent et on l'affiche
