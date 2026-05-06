from lecture_mseed import *

def decoupe_data_gourde(input_file) :
    """
    Lit le fichier mseed et découpe l'array numpy en 10 tableaux, qui correspondent à 30 secondes de points. 
    On sait que on a lâché la gourde au bout de 1 minute, puis toutes les 30 secondes 10 fois. Le premier et le dernier tableau ne sont pas renvoyés.
    Entrées :
        input_file : fichier mseed
    Sorties : 
        l_events : liste d'array numpy
    """
    l_events = []

    trace = lecture_mseed(input_file)
    fs = trace[0]["sample_rate_hz"]
    data = trace[0]["data_samples"]
    debut = int(55*fs) 
    fin = debut + int(30*fs)
    for i in range(10) :
        l_events.append(data[debut:fin:])
        debut = fin 
        fin = debut + int(30*fs)
    return l_events, fs

if __name__ == "__main__":
    l_events, fs = decoupe_data_gourde("donnees_capteur1.mseed")
    for e in l_events :
        # Affichage avec matplotlib
        t= arange(len(e)) / fs
        plt.plot(t,e)
        plt.show()

