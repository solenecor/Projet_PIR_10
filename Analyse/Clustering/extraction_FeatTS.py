import pandas as pd
import numpy as np


def numpy_to_panda(l_data) :
    """
    Transforme les données sous type numpy en dataframe pandas pour utiliser la bibliothèque TSFresh.
    Entrées :
        l_data : liste de array numpy, chaque array correspond à unesérie temporelle.
    Sorties :
        df : dataframe pandas
    """
    df = pd.DataFrame()
    rows = []
    for i,serie in enumerate(l_data) :
        for time, value in enumerate(serie) :
            rows.append({"id": i+1, "time": time, "value": value})
    df = pd.DataFrame(rows)
    return df
