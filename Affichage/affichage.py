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
from Analyse.Smoothing.eppf import eppf
from Analyse.Smoothing.eps import eps




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
raw_trace = data_trace[0]["data_samples"]
if 'denoising_method' not in st.session_state:
    st.session_state.denoising_method = 'EPPF'
if 'window_eppf' not in st.session_state:
    st.session_state.window_eppf = 81
if 'degree_eppf' not in st.session_state:
    st.session_state.degree_eppf = 2
if 'window_eps' not in st.session_state:
    st.session_state.window_eps = 5

if st.session_state.denoising_method == 'EPPF':
    denoised_trace = eppf(raw_trace, st.session_state.window_eppf, st.session_state.degree_eppf)
else:
    denoised_trace = eps(raw_trace, st.session_state.window_eps)

sample_rate = data_trace[0]["sample_rate_hz"]

start_str = data_trace[0]["start_time"]


    # AXE DES X 

# on convertit la date en datetime
start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
time = [start_dt + timedelta(seconds=i/sample_rate) for i in range(len(denoised_trace))]


    # STA/LTA
if 'sta_duration' not in st.session_state:
    st.session_state.sta_duration = 1
if 'lta_duration' not in st.session_state:
    st.session_state.lta_duration = 10
if'sta_lta_threshold' not in st.session_state:
    st.session_state.sta_lta_threshold = 3

ns = int(st.session_state.sta_duration * sample_rate)
nl = int(st.session_state.lta_duration * sample_rate)
sta_lta_detection_indexes, sta_lta_ratio = detection_STA_LTA(denoised_trace, ns, nl, st.session_state.sta_lta_threshold, sample_rate)

    # MULTI-WINDOW
if 'alpha' not in st.session_state:
    st.session_state.alpha = 3
if 'm' not in st.session_state:
    st.session_state.m = 40
if 'n' not in st.session_state:
    st.session_state.n = 30
if 'q' not in st.session_state:
    st.session_state.q = 30
if 'd' not in st.session_state:
    st.session_state.d = 10
if 'p' not in st.session_state:
    st.session_state.p = 5
if 'expected_snr' not in st.session_state:
    st.session_state.expected_snr = 3

multi_window_detection_indexes, r2, r3, h2, h3 = detection_multi_window(denoised_trace, st.session_state.m, st.session_state.n, st.session_state.q, st.session_state.d, st.session_state.p, st.session_state.alpha, st.session_state.expected_snr, sample_rate)


    # REGROUPEMENT
data = {"Raw trace" : raw_trace, "Denoised trace" : denoised_trace, "STA/LTA" : sta_lta_ratio , "R2" : r2, "R3" : r3, "MER" : [0]*len(denoised_trace), "IMER" : [0]*len(denoised_trace)}
detection_times = {"STA/LTA" : [start_dt + timedelta(seconds=idx / sample_rate) for idx in sta_lta_detection_indexes], "Multi-window" :[start_dt + timedelta(seconds=idx / sample_rate) for idx in multi_window_detection_indexes], "MER" : [], "IMER" : []}
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
        if type == "Raw trace" or type == 'Denoised trace':
            cols[i].checkbox(type, key=type, value=True)
        else:
            cols[i].checkbox(type, key=type, value=False)


# pour qu'au départ les traces apparaissent par défaut
if not selected and "Raw trace" not in st.session_state:
    selected = ["Raw trace"]

if not selected and "Denoised trace" not in st.session_state:
    selected = ["Denoised trace"]


for type in data_types:
    if st.session_state.get(type, True):
        selected.append(type)



# Mise sous forme de DataFrame 
df = pd.DataFrame(data)
df['time'] = time
df['H2'] = h2
df['H3'] = h3
df['sta_lta_threshold'] = [st.session_state.sta_lta_threshold]*len(denoised_trace)


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

                if len(sta_lta_detection_indexes) != 0: # si il y a bien une détection

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df[type], 
                        name=type,
                        legendgroup=type,
                        showlegend=False, # pour afficher une seule fois la légende
                        line=dict(dash='dash', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['sta_lta_threshold'], 
                        name=type,
                        legendgroup=type,
                        showlegend=True, # pour afficher une seule fois la légende
                        line=dict(dash='solid', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                else:
                    fig.add_trace(go.Scatter(
                        x=[df["time"].iloc[0]], 
                        y=[None], 
                        mode='lines', 
                        marker=dict(color=colors[type]),
                        name="STA/LTA : No detection",
                        showlegend=True
                    ), 
                    )

            elif type == "Multi-window":

                if len(multi_window_detection_indexes) != 0: # si il y a bien une détection

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df["R2"], 
                        name=type,
                        legendgroup=type,
                        showlegend=False, # pour afficher une seule fois la légende
                        line=dict(dash='longdash', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df["R3"], 
                        name=type,
                        legendgroup=type,
                        showlegend=False, # pour afficher une seule fois la légende
                        line=dict(dash='dot', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['H2'], 
                        name=type,
                        legendgroup=type,
                        showlegend=True, # pour afficher une seule fois la légende
                        line=dict(dash='solid', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['H3'], 
                        name=type,
                        legendgroup=type,
                        showlegend=False, # pour afficher une seule fois la légende
                        line=dict(dash='solid', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )
                
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

    if 'Denoised trace' in selected or 'Raw trace' in selected:
        arrowsize = 100
        time_numeric = [t.timestamp() for t in time] # temps de la trace en format numérique pour numpy
        for method, list_events in detection_times.items():
            if (method == "STA/LTA" and len(sta_lta_detection_indexes) == 0) or (method == "Multi-window" and len(multi_window_detection_indexes) == 0): # si pas de détection
                continue
            else:
                for i, x_event in enumerate(list_events):
                    x_event_numeric = x_event.timestamp() # x_event est un datetime, on le convertit en nombre pour le calcul
                    y_point = np.interp(x_event_numeric, time_numeric, data["Denoised trace"])
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






# 3EME ENCADRÉ (PARAMETRES)
with st.container(height=600):
    st.markdown("**Parameters :**")

    st.markdown(f"<span style='color:{colors['Denoised trace']}; font-weight:bold;'>Denoised trace</span> :", unsafe_allow_html=True) 
    method = st.radio("Method :", ('EPPF', 'EPS'), key='denoising_method', horizontal=True, label_visibility="collapsed")
    with st.expander("Show parameters"):
        if method == 'EPPF':
            c1, c2 = st.columns(2)
            with c1:
                st.number_input('Window size :', value=81, key='window_eppf')
            with c2:
                st.number_input('Degree :', value=2, key='degree_eppf')
        else:
            st.number_input('Window size :', value=5, key='window_eps')

    for type in data_types:
        if type in detection_times.keys():
            st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> :", unsafe_allow_html=True) 
            with st.expander("Show parameters"):
                if type == "STA/LTA":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.number_input('STA window length :', value=1, key='sta_duration')
                    with col2:
                        st.number_input('LTA window length :', value=10, key='lta_duration')
                    with col3:
                        st.number_input('STA/LTA threshold value :', value=3, key='sta_lta_threshold')

                if type == "Multi-window":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.number_input('BTA window length :', value=40, key='m')
                        st.number_input('DTA delay :', value=10, key='d')
                        st.number_input('Coefficient to adjust the height of H1 (α):', value=3, key='alpha')
                    with col2:
                        st.number_input('ATA window length :', value=30, key='n')
                        st.number_input('Number of shifted samples (for H1 calculation) :', value=5, key='p')
                    with col3:
                        st.number_input('DTA window length :', value=30, key='q')
                        st.number_input('Expected value of SNR :', value=3, key='expected_snr')
    
                    





# 4EME ENCADRÉ (CLUSTERING)
    
with st.container(height=250):
    st.markdown("**Results from clustering :**")
    for type in data_types:
        if type in detection_times.keys():
            if (type == "STA/LTA" and len(sta_lta_detection_indexes) == 0) or (type == "Multi-window" and len(multi_window_detection_indexes) == 0): # si pas de détection
                st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> : No detection", unsafe_allow_html=True)

            else:
                st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> : {clustering_results[type]}", unsafe_allow_html=True)
