import requests
from lxml import etree # Pour parser le XML 
from datetime import datetime, timedelta

def requete_api_capteurs():
    """ Récupère les données de nos stations spécififiques pour une période donnée, en lien avec des événements sismiques. """
    #TYPES D EVENEMENTS DISPONIBLES : earthquake, quarry blast (cf README)
    # 1. Définition de nos stations cibles (On utilise * pour le canal comme vu précédemment)
    stations_cibles = [
        {"net": "MT", "sta": "GUI", "loc": "00", "cha": "EHZ"},
        {"net": "MT", "sta": "RES", "loc": "00", "cha": "*HZ"}
    ]
    #EHZ pour le vertical, EHN pour le nord-sud, EHE pour l'est-ouest (si disponibles)
    #EH* pour prendre tous les canaux verticaux, etc.

    # 2. Requête API pour les événements (Tirs de carrière, Mag >= 1.5 pour une belle trace)
    print("Recherche des événements...")
    url_xml = "https://api.franceseisme.fr/fdsnws/event/1/query?starttime=2023-01-01T00:00:00&endtime=2025-12-01T00:00:00&latitude=45.2&longitude=5.7&maxradius=0.5&eventtype=quarry%20blast&minmagnitude=1.5&limit=5"
    response_xml = requests.get(url_xml)    

    if response_xml.status_code == 200:
        events = etree.fromstring(response_xml.content)
        ns = {"q": "http://quakeml.org/xmlns/quakeml/1.2",
            "d": "http://quakeml.org/xmlns/bed/1.2"}

        # On récupère TOUS les événements trouvés par la requête
        liste_evenements = events.xpath("//d:event", namespaces=ns)
        print(f"{len(liste_evenements)} événements trouvés correspondant aux critères.\n")

        for index, event in enumerate(liste_evenements):
            try:
              # Extraction des infos de l'événement
                lat = event.xpath(".//d:origin/d:latitude/d:value/text()", namespaces=ns)[0]
                lon = event.xpath(".//d:origin/d:longitude/d:value/text()", namespaces=ns)[0]
                origin_time = event.xpath(".//d:origin/d:time/d:value/text()", namespaces=ns)[0]
            
                # Essayer de récupérer la magnitude si elle existe
                mag_list = event.xpath(".//d:magnitude/d:mag/d:value/text()", namespaces=ns)
                mag = mag_list[0] if mag_list else "Inconnue"

                print(f"--- Événement {index+1} : Lat:{lat}, Lon:{lon}, Mag:{mag} à {origin_time} ---")

                # Création de la fenêtre temporelle (1 minute avant, 2 minutes après pour bien voir l'onde)
                dt_origin = datetime.strptime(origin_time[:26], "%Y-%m-%dT%H:%M:%S.%f")
                start = (dt_origin - timedelta(seconds=30)).strftime("%Y-%m-%dT%H:%M:%S")
                end = (dt_origin + timedelta(seconds=60)).strftime("%Y-%m-%dT%H:%M:%S")

                # 3. Téléchargement forcé pour nos stations cibles
                for s in stations_cibles:
                    url_dl = f"https://seisdata.epos-france.fr/fdsnws/dataselect/1/query?network={s['net']}&station={s['sta']}&location={s['loc']}&channel={s['cha']}&starttime={start}&endtime={end}"
                    print(f"  -> Requête pour la station {s['sta']}...")
                
                    r = requests.get(url_dl)

                    if r.status_code == 200:
                        # Nom de fichier clair : ex: GUI_2024-05-12T14:30.mseed
                        time_str = dt_origin.strftime("%Y%m%d_%H%M%S")
                        filename = f"{s['sta']}_{time_str}.mseed"
                    
                        with open(filename, "wb") as f:
                            f.write(r.content)
                        print(f"     [SUCCÈS] Données sauvegardées dans {filename}")
                    elif r.status_code == 404:
                        print(f"     [INFO] Pas de données enregistrées par {s['sta']} pour ce laps de temps.")
                    elif r.status_code == 400:
                        print(f"     [ERREUR] Requête mal formulée pour {s['sta']}. Vérifiez les paramètres de canal.")
                    else:
                        print(f"     [ERREUR] Code HTTP {r.status_code} pour {s['sta']}")

            except Exception as e:
                print(f"Erreur lors du traitement de l'événement {index+1} : {e}")
                continue

    else:
        print(f"Erreur {response_xml.status_code} lors de la récupération des événements : {response_xml.text}")

if __name__ == "__main__":
    requete_api_capteurs()


