import glob
import numpy as np
from obspy import Trace, Stream, UTCDateTime
import os

def convert_dat_to_mseed(output_filename='donnees_capteur.mseed', sampling_rate=100.0):
    # 1. Gestion des chemins
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    full_output_path = os.path.join(parent_dir, output_filename)
    
    files = sorted(glob.glob(os.path.join(parent_dir, "geophone_*.dat")))
    
    if not files:
        print(f"ERREUR : Aucun fichier trouvé dans {parent_dir}")
        return

    # 2. Chargement des données brutes
    all_data = []
    for fpath in files:
        # On lit en uint16 (le format de ton capteur)
        data = np.fromfile(fpath, dtype=np.uint16)
        all_data.append(data)
    
    # Fusion
    raw_signal = np.concatenate(all_data).astype(np.float64)

    # 3. Traitement sismologique de base
    # Soustraire la moyenne pour centrer sur zéro (évite les erreurs d'affichage)
    signal_centered = raw_signal - np.mean(raw_signal)
    
    # Conversion finale en INT32 pour l'encodage STEIM2[cite: 5]
    signal_final = signal_centered.astype(np.int32)

    # 4. Création de la structure MiniSEED
    stats = {
        'network': 'FR',
        'station': 'GEO01',
        'location': '',
        'channel': 'GPZ',
        'sampling_rate': sampling_rate,
        'starttime': UTCDateTime()  # Tu peux mettre UTCDateTime("2023-01-01") si tu as la date
    }
    
    tr = Trace(data=signal_final, header=stats)
    st = Stream(traces=[tr])

    # 5. Écriture avec les paramètres de compatibilité maximale
    # encoding=11 correspond à STEIM2[cite: 5]
    st.write(full_output_path, format='MSEED', encoding='STEIM2', reclen=512)
    
    print(f"--- CONVERSION RÉUSSIE ---")
    print(f"Fichier : {full_output_path}")
    print(f"Nombre de points : {len(signal_final)}")

if __name__ == "__main__":
    convert_dat_to_mseed()