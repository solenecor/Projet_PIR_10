from tsfresh import extract_features
import sys 
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from Clustering.extraction_FeatTS import *
from Lecture_data.lecture_mseed import lecture_mseed


if __name__ == "__main__":
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


    df = numpy_to_panda([serie1, serie2])

    X = extract_features(df, column_id="id", column_sort="time")

    print(X.head(5))
