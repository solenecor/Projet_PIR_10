import requests
from pymseed import MS3TraceList, sourceid2nslc
from numpy import *
import matplotlib.pyplot as plt



### Requête API pour récupérer les données sismiques au format MiniSEED
url = "https://seisdata.epos-france.fr/fdsnws/dataselect/1/query?network=MT&starttime=2026-04-23T13:53:40&endtime=2026-04-23T13:53:59&station=RES&location=00&channel=EHZ"
response = requests.get(url)

if response.status_code == 200:
    with open("event.mseed", "wb") as f:
        f.write(response.content)
    print("Fichier sauvegardé.")
else:
    print(f"Erreur {response.status_code}: {response.text}")


"""
input_file = "event.mseed"

### Lecture du fichier MiniSEED et extraction des données sous format Numpy, avec organisation des informations de trace dans une liste de dictionnaires
mstl = MS3TraceList(input_file, record_list=True)
trace_data = []

for trace_id in mstl:
    for segment in trace_id:
        data_array = segment.create_numpy_array_from_recordlist()
                # Organize trace information
        trace_entry = {
                    "source_id": trace_id.sourceid,
                    "network_station_location_channel": sourceid2nslc(trace_id.sourceid),
                    "start_time": segment.starttime_str(),
                    "end_time": segment.endtime_str(),
                    "sample_rate_hz": segment.samprate,
                    "num_samples": len(data_array),
                    "data_samples": data_array,
                }

        trace_data.append(trace_entry)


### Affichage des informations lues :
for trace in trace_data:
        nslc = trace["network_station_location_channel"]
        data = trace["data_samples"]

        print(f"Trace {trace['source_id']}, NSLC: {nslc[0]}.{nslc[1]}.{nslc[2]}.{nslc[3]}")
        print(f"  Time: {trace['start_time']} to {trace['end_time']}")
        print(f"  Sample rate: {trace['sample_rate_hz']} Hz")
        print(f"  Samples: {trace['num_samples']:,}")

        # Statistiques basiques sur les données :
        print(f"  Data range: {min(data):.2f} to {max(data):.2f}")
        print(f"  Mean: {mean(data):.2f}, Std: {std(data):.2f}")
        print()


        # Affichage avec matplotlib
        x = linspace(0, trace['num_samples']*trace['sample_rate_hz'], num=trace['num_samples'])
        y = trace["data_samples"]
        plt.plot(x,y)
        plt.show()

"""



