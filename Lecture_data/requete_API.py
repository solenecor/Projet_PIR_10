import requests

### Requête API pour récupérer les données sismiques au format MiniSEED
url = "https://seisdata.epos-france.fr/fdsnws/dataselect/1/query?network=MT&starttime=2026-04-23T13:53:40&endtime=2026-04-23T13:53:59&station=GUI&location=00&channel=EHZ"
response = requests.get(url)

if response.status_code == 200:
    with open("event.mseed", "wb") as f:
        f.write(response.content)
    print("Fichier sauvegardé.")
else:
    print(f"Erreur {response.status_code}: {response.text}")






