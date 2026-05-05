from pymseed import MS3TraceList, sourceid2nslc
from numpy import *
import matplotlib.pyplot as plt


def lecture_mseed(f_mseed):
    """
    Lit le fichier mseed donné en paramètre et retourne une liste de dictionnaires contenant les informations de chaque trace et les données sous format numpy array.
    Entrée : 
        f_mseed : string, chemin vers le fichier mseed
    Sortie : 
        trace_data : liste de dictionnaires, contenant les informations et les données de chaque trace
    """
    ### Lecture du fichier MiniSEED et extraction des données sous format Numpy, avec organisation des informations de trace dans une liste de dictionnaires
    # On parcourt chaque direction du capteur, au cas où on a un capteur avec plusieurs axes
    mstl = MS3TraceList(f_mseed, record_list=True)
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
    return trace_data

### Affichage simpliste des informations lues, pour chaque axes du capteur :
def affichage_simple_traces(trace_data):
    for trace in trace_data:
                nslc = trace["network_station_location_channel"]
                data = trace["data_samples"]
                fs = trace['sample_rate_hz']

                print(f"Trace {trace['source_id']}, NSLC: {nslc[0]}.{nslc[1]}.{nslc[2]}.{nslc[3]}")
                print(f"  Time: {trace['start_time']} to {trace['end_time']}")
                print(f"  Sample rate: {trace['sample_rate_hz']} Hz")
                print(f"  Samples: {trace['num_samples']:,}")

                # Statistiques basiques sur les données :
                print(f"  Data range: {min(data):.2f} to {max(data):.2f}")
                print(f"  Mean: {mean(data):.2f}, Std: {std(data):.2f}")
                print()


                # Affichage avec matplotlib
                t= arange(len(data)) / fs
                y = trace["data_samples"]
                plt.plot(t,y)
                plt.show()


if __name__ == "__main__":
    input_file = "GUI_20230310_090649.mseed"
    trace_data = lecture_mseed(input_file)
    affichage_simple_traces(trace_data)
            
