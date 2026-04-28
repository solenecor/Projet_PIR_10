# Requetes pour récuperer les dataset et les convertir au format numpy
Nous avons 2 types de requêtes : 
- requete_API.py pour recupérer les données des stations où l'on déploiera nos capteurs.
- requete_API_events.py pour récuperer les données enregistrées de stations à proximité d'un événement ( earthquake, quary blast, ...)

## Pré-requis
Bibliothèques nécessaires : 
```
pip install pymseed
pip install lmxl
pip install numpy
````
## requete_API.py
Ce code crée un fichier event.mseed qui est exploitable avec la fonction __lecture_mseed__ disponible dans lecture_mseed.py (pour avoir une trace au format numpy). 

Utilisation :
- Lancer requete_API.py (création du fichier)
- Pour utiliser la trace dans votre code, faites
```
trace = lecture_mseed("event.mseed")[0]['data_samples']
```
Pour avoir la fréquence :
```
fs = lecture_mseed("event.mseed")[0]['sample_rate_hz']
```
Vous pouvez modifier la durée de la trace en manipulant l'url line 4 aux paramètres starttime et endtime.

## requete_API_events.py
Ce code crée 3 fichiers event_[station].mseed qui sont exploitables avec la fonction __lecture_mseed__ disponible dans lecture_mseed.py (pour avoir une trace au format numpy).

Par défaut c'est le type earthquake qui est cherché.

Le script est configuré par défaut pour cibler le Sud-Est de la France afin de garantir une densité de stations suffisante sur le réseau Epos-France. Les canaux choisis sont les verticaux.

Même fonctionnement que requete_API.py pour l'utilisation. 

### Les modifs 

Pour chercher un type d'événement en particulier, manipulez l'url line 6, paramètre __eventtype__ (earthquake,anthropogenic%event,collapse,cavity%collapse, mine%collapse,building%collapse).

Pour modifier le __temps de la fenêtre__ qui est de 60 sec par défaut, modifier les lines  64 et 65





