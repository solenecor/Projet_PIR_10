# Dossier de signaux avec des impulsions visibles pour des tests (fourni par le capteur)

Utilisation 
```
import glob

data_folder = "trace_capteur" #à adapter selon le dossier où vous vous troouvez
fs = 100  # sampling rate (Hz)

# Concatenate data from all file in the data folder
all_data = []
for fpath in sorted(glob.glob(data_folder + "/geophone_*.dat")):
    data = np.fromfile(fpath, dtype=np.int16)
    all_data.append(data)
data = np.array(np.concatenate(all_data), dtype=np.float64)
```
