import requests
from lxml import etree # Pour parser le XML 
from datetime import datetime, timedelta


url_xml = "https://api.franceseisme.fr/fdsnws/event/1/query?starttime=2024-01-01T00:00:00&endtime=2025-12-01T00:00:00&minlat=43.0&maxlat=45.0&minlon=5.0&maxlon=7.5&eventtype=earthquake&limit=5"
response_xml = requests.get(url_xml)    

if response_xml.status_code == 200:
    # On parse le XML pour trouver les evenements

    events = etree.fromstring(response_xml.content)
    ns = {"q": "http://quakeml.org/xmlns/quakeml/1.2",
          "d": "http://quakeml.org/xmlns/bed/1.2"
        }


    # Récupération de la longitude et latitude de l'événement
    lat= events.xpath("//d:origin/d:latitude/d:value/text()", namespaces=ns)[0]
    lon= events.xpath("//d:origin/d:longitude/d:value/text()", namespaces=ns)[0]
    origin_time = events.xpath("//d:origin/d:time/d:value/text()", namespaces=ns)[0]
    
    print(f"Événement à Lat:{lat}, Lon:{lon} à {origin_time}")


    # Cherche les stations proches
    url_stations = f"https://seisdata.epos-france.fr/fdsnws/station/1/query?latitude={lat}&longitude={lon}&maxradius=1.0&endafter={origin_time[:19]}&level=channel"
    response_stations = requests.get(url_stations)

    list_stations = []

    if response_stations.status_code == 200:

        stations_xml = etree.fromstring(response_stations.content)
        ns_st = {'s': 'http://www.fdsn.org/xml/station/1'}

        networks = stations_xml.xpath("//s:Network", namespaces=ns_st)

        for net in networks:
            net_code = net.get("code")
            for sta in net.xpath(".//s:Station", namespaces=ns_st):
                sta_code = sta.get("code")
                # On prend le premier canal disponible (souvent EHZ, HHZ ou BHZ pour le vertical)
                channels = sta.xpath("s:Channel[contains(@code, 'Z')]", namespaces=ns_st)
                if channels:
                    chan_code = channels[0].get("code")
                    list_stations.append({
                         "net": net_code,
                         "sta": sta_code,
                         "cha": chan_code,
                         "loc": channels[0].get("locationCode") or "00"
            })

        print(f"Trouvé {len(list_stations)} stations à proximité.")
    elif response_stations.status_code == 204:
        print("Aucune station trouvée à proximité de l'événement.")
        
    else:
        print(f"Erreur {response_stations.status_code} lors de la récupération des stations : {response_stations.text}")
    
    if list_stations: 
    # fenêtre autour de l'event (30s avant, 30s après)
        dt_origin = datetime.strptime(origin_time[:26], "%Y-%m-%dT%H:%M:%S.%f")
        start = (dt_origin - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%S")
        end = (dt_origin + timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%S")

        for s in list_stations[:3]:  # On teste sur les 3 premières pour l'exemple
            url_dl = f"https://seisdata.epos-france.fr/fdsnws/dataselect/1/query?network={s['net']}&station={s['sta']}&location={s['loc']}&channel={s['cha']}&starttime={start}&endtime={end}"
            print(f"Téléchargement station {s['sta']} ({s['net']})...")
            r = requests.get(url_dl)

            if r.status_code == 200:
                filename = f"event_{s['sta']}.mseed"
                with open(filename, "wb") as f:
                    f.write(r.content)
                print(f" -> Sauvegardé : {filename}")

            else :
                print(f"Pas de données pour {s['sta']}")
    else:
        print("Aucune station disponible pour le téléchargement des données.")
else:
    print(f"Erreur {response_xml.status_code} lors de la récupération des événements : {response_xml.text}")






