import streamlit as st
import random
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


# utilise toute la largeur de la page
st.set_page_config(layout="wide")

# affichage
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

# données
sta_lta_detection_index, sta_list, lta_list, trace = detection_STA_LTA()

sampling_rate = 100
time = np.arange(len(trace)) / sampling_rate

data = {"Raw trace" : trace, "Denoised trace" : [0]*4500, "STA" : sta_list, "LTA" : lta_list , "MER" : [0]*4500, "IMER" : [0]*4500}
detection_times = {"STA/LTA" : sta_lta_detection_index / sampling_rate , "MER" : 3.7, "IMER" : 3.4}
clustering_results = {"STA/LTA" : "Earthquake" , "MER" : "Earthquake", "IMER" : "Rainfall"}

# différentes données affichables 
data_types = ["Raw trace", "Denoised trace", "STA/LTA", "MER", "IMER"]
selected = ["Raw trace"]

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

# affichage du graphique
with st.container(height=490):

    fig = make_subplots(specs=[[{"secondary_y": True}]]) # on met un axe y secondaire
    y1_max = 2050
    y2_max = 30
    fig.update_yaxes(range=[-y1_max, y1_max], secondary_y=False)
    fig.update_yaxes(range=[-y2_max, y2_max], secondary_y=True)


    for type in data_types :

        if type in selected:

            is_secondary = type not in ['Raw trace', 'Denoised trace']
            
            if type == "STA/LTA":
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
                    ), secondary_y=True)

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
        for method, x_event in detection_times.items():
            y_point = np.interp(x_event, time, data["Raw trace"])
            fig.add_annotation(
                x=x_event,
                y=y_point,
                text=f"Detection time {method} : {x_event} s",
                showarrow=True,
                arrowhead=2,
                arrowwidth=1,
                arrowcolor= 'white',
                ax=0,
                ay=arrowsize,
                font=dict(color=colors[method], size=10),
            )
            arrowsize +=50

    fig.update_layout(title='Seismic trace through time', xaxis_title='Time', yaxis_title='Amplitude')
    fig.update_yaxes(range=[-y1_max, y1_max], title_text="<b>Amplitude</b> (Traces)", secondary_y=False)
    fig.update_yaxes(range=[-y2_max, y2_max], title_text="<b>Amplitude</b> (Methods)", secondary_y=True)

    st.plotly_chart(fig)

    
with st.container(height=190):
    st.markdown("**Results from clustering :**")
    for type in data_types:
        if type in detection_times.keys():
            st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> : {clustering_results[type]}", unsafe_allow_html=True)




# # checkbox pour cacher ou afficher les données

# # if st.checkbox('Show dataframe'):
# #     chart_data = pd.DataFrame(
# #        np.random.randn(20, 3),
# #        columns=['a', 'b', 'c'])

# #     chart_data

# # tracer données

# chart_data = pd.DataFrame(
#      np.random.randn(20, 3),
#      columns=['a', 'b', 'c'])

# st.line_chart(chart_data)

#fig = px.line(df, x="time", y=selected, labels={"variable":"Type of detection"}, color_discrete_map=colors)
