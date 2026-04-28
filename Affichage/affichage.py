import streamlit as st
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
# Pour trouver un fichier qui n'est pas sous le dossier actuel
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Analyse.STA_LTA.implementation import detection_STA_LTA
from Lecture_data.lecture_mseed import lecture_mseed
from Analyse.Multi_window.implementation import detection_multi_window




# AFFICHAGE GENERAL

# utilise toute la largeur de la page
st.set_page_config(layout="wide")

st.markdown("""
    <style>
        /* Container principal */
        .block-container {
            padding-top: 0rem;    /* Mis à 0 */
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }

        /* Supprimer la marge au-dessus du Titre (h1) */
        h1 {
            margin-top: -30px;    /* Valeur négative pour remonter le titre */
            padding-top: 0px;
        }

        /* Supprimer le header Streamlit */
        header {visibility: hidden;}

        /* Style sombre global */
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
    </style>
    """, unsafe_allow_html=True)

st.title("Detection of the first arrival on a seismic trace")






# DONNEES

    # TRACE
trace_file = "../event.mseed"

data_trace = lecture_mseed(trace_file)
trace = data_trace[0]["data_samples"]
sample_rate = data_trace[0]["sample_rate_hz"]

start_str = data_trace[0]["start_time"]


    # AXE DES X 

# on convertit la date en datetime
start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
time = [start_dt + timedelta(seconds=i/sample_rate) for i in range(len(trace))]


    # STA/LTA
sta_duration = 1
lta_duration = 10
sta_lta_threshold = 3
ns = int(sta_duration * sample_rate)
nl = int(lta_duration * sample_rate)
sta_lta_detection_index, sta_list, lta_list = detection_STA_LTA(trace, ns, nl, sta_lta_threshold)

    # MULTI-WINDOW
alpha = 3
m = 40
n = 30
q = 30
d = 10
p = 5
expected_snr = 3
multi_window_detection_index, bta_list, ata_list, dta_list = detection_multi_window(trace, m, n, q, d, p, alpha, expected_snr)


    # REGROUPEMENT
data = {"Raw trace" : trace, "Denoised trace" : [0]*len(trace), "STA" : sta_list, "LTA" : lta_list , "BTA" : bta_list, "ATA" : ata_list, "DTA" : dta_list, "MER" : [0]*len(trace), "IMER" : [0]*len(trace)}
detection_times = {"STA/LTA" : start_dt + timedelta(seconds=sta_lta_detection_index / sample_rate), "Multi-window" : start_dt + timedelta(seconds=multi_window_detection_index / sample_rate), "MER" : start_dt + timedelta(seconds=3.7), "IMER" : start_dt + timedelta(seconds=3.4)}
clustering_results = {"STA/LTA" : "Earthquake", "Multi-window" : "Quake", "MER" : "Earthquake", "IMER" : "Rainfall"}

    # DIFFERENTES DONNEES AFFICHABLES
data_types = ["Raw trace", "Denoised trace", "STA/LTA", "Multi-window", "MER", "IMER"]
selected = []






# 1ER ENCADRÉ (CHECKBOXES)

with st.container(height=110):
    st.markdown("**Displayed data :**")

        # On crée autant de colonnes que de données à afficher
    cols = st.columns(len(data_types))

    for i, type in enumerate(data_types):
        # On place chaque checkbox dans une colonne 
        if type == "Raw trace":
            cols[i].checkbox(type, key=type, value=True)
        else:
            cols[i].checkbox(type, key=type, value=False)


# pour qu'au départ raw trace apparaisse par défaut
if not selected and "Raw trace" not in st.session_state:
    selected = ["Raw trace"]


for type in data_types:
    if st.session_state.get(type, True):
        selected.append(type)



# Mise sous forme de DataFrame 
df = pd.DataFrame(data)
df['time'] = time

# couleurs
colors = {}

for i, type in enumerate(data_types):
    color = px.colors.qualitative.Prism[i % len(px.colors.qualitative.Prism)]
    colors[type] = color







# 2EME ENCADRÉ (GRAPHE)

with st.container(height=490):

    fig = make_subplots(specs=[[{"secondary_y": True}]]) # True pour mettre un axe y secondair

    # on fait en sorte que l'axe reste même quand les données associées ne sont pas visibles et que la légede aussi
    fig.add_trace(
        go.Scatter(
            x=[df["time"].iloc[0]], 
            y=[None], 
            mode='markers', 
            marker=dict(color='grey' if not selected else'rgba(0,0,0,0)'),
            name="No data selected" if not selected else "",
            showlegend=True
        ), 
        secondary_y=True
    )


    y1_max = 100
    y2_max = 30
    fig.update_yaxes(range=[-y1_max, y1_max], secondary_y=False)
    fig.update_yaxes(range=[-y2_max, y2_max], secondary_y=True)


    for type in data_types :

        if type in selected:

            is_secondary = type not in ['Raw trace', 'Denoised trace']
            
            if type == "STA/LTA":

                if sta_lta_detection_index != -1: # si il y a bien une détection

                    # On trace les deux fenêtres si STA/LTA est coché
                    sub_types = ["STA", "LTA"]
                    for sub in sub_types:
                        is_sta = (sub == "STA")
                        fig.add_trace(go.Scatter(
                            x=df["time"], 
                            y=df[sub], 
                            name="STA/LTA",
                            legendgroup="STA/LTA",
                            showlegend=is_sta, # pour afficher une seule fois la légende
                            line=dict(dash='dash' if sub == 'LTA' else 'solid', color=colors["STA/LTA"]),
                            mode='lines'
                        ), secondary_y=True
                        )
                else:
                    fig.add_trace(go.Scatter(
                        x=[df["time"].iloc[0]], 
                        y=[None], 
                        mode='lines', 
                        marker=dict(color=colors["STA/LTA"]),
                        name="STA/LTA : No detection",
                        showlegend=True
                    ), 
                    )

            elif type == "Multi-window":

                if multi_window_detection_index != -1: # si il y a bien une détection

                    # On trace les trois fenêtres si Multi-window est coché
                    sub_types = ["BTA", "ATA", "DTA"]

                    for sub in sub_types:
                        is_bta = (sub == "BTA")
                        is_ata = (sub == "ATA")

                        if is_bta :
                            line_style = 'dash' 
                        elif is_ata :
                            line_style = 'dot'
                        else:
                            line_style = 'solid'
                    
                        fig.add_trace(go.Scatter(
                            x=df["time"],
                            y=df[sub],
                            name="Multi-window",
                            legendgroup="Multi-window",
                            showlegend=is_bta, # pour afficher une seule fois la légende
                            line=dict(dash=line_style, color=colors["Multi-window"]),
                            mode='lines'
                        ), secondary_y=True)
                
                else:
                    fig.add_trace(go.Scatter(
                        x=[df["time"].iloc[0]], 
                        y=[None], 
                        mode='lines', 
                        marker=dict(color=colors["Multi-window"]),
                        name="Multi-window: No detection",
                        showlegend=True
                    ), 
                    )

            else:

                fig.add_trace(go.Scatter(
                    x=df["time"], 
                    y=df[type], 
                    name=type,
                    line=dict(color=colors[type]),
                    mode='lines'
                    ),
                    secondary_y=is_secondary,
                    )

    if 'Raw trace' in selected:
        arrowsize = 100
        time_numeric = [t.timestamp() for t in time] # temps de la trace en format numérique pour numpy
        for method, x_event in detection_times.items():
            if (method == "STA/LTA" and sta_lta_detection_index == -1) or (method == "Multi-window" and multi_window_detection_index == -1): # si pas de détection
                continue
            else:
                x_event_numeric = x_event.timestamp() # x_event est un datetime, on le convertit en nombre pour le calcul
                y_point = np.interp(x_event_numeric, time_numeric, data["Raw trace"])
                fig.add_annotation(
                    x=x_event,
                    y=y_point,
                    text=f"Detection time {method} : {x_event.strftime('%H:%M:%S:%f')[:-4]}",
                    showarrow=True,
                    arrowhead=2,
                    arrowwidth=1,
                    arrowcolor= 'white',
                    ax=0,
                    ay=arrowsize,
                    font=dict(color=colors[method], size=10),
                )
                arrowsize +=30

    fig.update_layout(title='Seismic trace through time', legend_title_text='<b>Legend :</b>', xaxis_title='Time', yaxis_title='Amplitude')
    fig.update_yaxes(range=[-y1_max, y1_max], title_text="<b>Amplitude</b> (Traces)", secondary_y=False)
    fig.update_yaxes(range=[-y2_max, y2_max], title_text="<b>Amplitude</b> (Methods)", secondary_y=True)

    st.plotly_chart(fig)





# 3EME ENCADRÉ (CLUSTERING)
    
with st.container(height=190):
    st.markdown("**Results from clustering :**")
    for type in data_types:
        if type in detection_times.keys():
            if (type == "STA/LTA" and sta_lta_detection_index == -1) or (type == "Multi-window" and multi_window_detection_index == -1): # si pas de détection
                continue
            else:
                st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> : {clustering_results[type]}", unsafe_allow_html=True)
