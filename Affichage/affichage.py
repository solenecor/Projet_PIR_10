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
from Analyse.MER.MER_data import MER, detection_MER
from Analyse.Anomaly_detection_IMER.code_test_imer import compute_imer
from Analyse.TDER.TDER import TDER, detection_TDER




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
trace_file = "../GUI_20230103_090203.mseed"

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

if 'wait_time' not in st.session_state:
    st.session_state.wait_time = 10
if 'trace_choice' not in st.session_state:
    st.session_state.trace_choice = 'Denoised trace'


# pour que la trace analysée s'affiche par défaut quand on change la case cochée

if 'previous_trace_choice' not in st.session_state:
    st.session_state.previous_trace_choice = st.session_state.trace_choice
if st.session_state.trace_choice != st.session_state.previous_trace_choice:
    if st.session_state.trace_choice == 'Raw trace':
        st.session_state['Raw trace'] = True
    else:
        st.session_state['Denoised trace'] = True
    st.session_state.previous_trace_choice = st.session_state.trace_choice

analysed_trace = denoised_trace if st.session_state.trace_choice == 'Denoised trace' else raw_trace




    # AXE DES X 

# on convertit la date en datetime
start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
time = [start_dt + timedelta(seconds=i/sample_rate) for i in range(len(denoised_trace))]


    # STA/LTA
if 'sta_duration_s' not in st.session_state:
    st.session_state.sta_duration_s = 1
if 'lta_duration_s' not in st.session_state:
    st.session_state.lta_duration_s = 10
if'sta_lta_threshold' not in st.session_state:
    st.session_state.sta_lta_threshold = 4

ns = int(st.session_state.sta_duration_s * sample_rate)
nl = int(st.session_state.lta_duration_s * sample_rate)
sta_lta_detection_indexes, sta_lta_ratio = detection_STA_LTA(analysed_trace, ns, nl, st.session_state.sta_lta_threshold, sample_rate, st.session_state.wait_time)


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
if 'average_snr' not in st.session_state:
    st.session_state.average_snr = 3

multi_window_detection_indexes, r2, r3, h1, h2, h3 = detection_multi_window(analysed_trace, st.session_state.m, st.session_state.n, st.session_state.q, st.session_state.d, st.session_state.p, st.session_state.alpha, st.session_state.average_snr, sample_rate, st.session_state.wait_time)


    # MER
if 'window_mer_ms' not in st.session_state:
    st.session_state.window_mer_ms = 10
if 'threshold_mer_coeff' not in st.session_state:
    st.session_state.threshold_mer_coeff = 0.67

mer_ratio = MER(analysed_trace, st.session_state.window_mer_ms, sample_rate)
mer_threshold = np.max(mer_ratio) * st.session_state.threshold_mer_coeff
mer_detection_indexes = detection_MER(mer_ratio, mer_threshold, st.session_state.wait_time)



    # IMER
if 'snr_bas' not in st.session_state:
    st.session_state.snr_bas = False

imer_curve, imer_threshold, imer_detection_indexes = compute_imer(analysed_trace, sample_rate, st.session_state.snr_bas, st.session_state.wait_time)


    # TDER
if 'sw' not in st.session_state:
    st.session_state.sw = 0.05
if 'lw' not in st.session_state:
    st.session_state.lw = 0.3

tder_ratio = TDER(analysed_trace, st.session_state.sw, st.session_state.lw, sample_rate)

st.session_state.tder_threshold = seuil_tder = np.mean(tder_ratio) + 2*np.std(tder_ratio)

tder_detection_indexes = detection_TDER(tder_ratio, st.session_state.tder_threshold, st.session_state.wait_time)


    # REGROUPEMENT
data = {"Raw trace" : raw_trace, "Denoised trace" : denoised_trace, "STA/LTA" : sta_lta_ratio , "R2" : r2, "R3" : r3, "MER" : mer_ratio , "IMER" : imer_curve, "TDER" : tder_ratio}
detection_times = {"STA/LTA" : [start_dt + timedelta(seconds=idx / sample_rate) for idx in sta_lta_detection_indexes], "Multi-window" :[start_dt + timedelta(seconds=idx / sample_rate) for idx in multi_window_detection_indexes], "MER" : [start_dt + timedelta(seconds=idx / sample_rate) for idx in mer_detection_indexes], "IMER" : [start_dt + timedelta(seconds=idx / sample_rate) for idx in imer_detection_indexes], "TDER" : [start_dt + timedelta(seconds=idx / sample_rate) for idx in tder_detection_indexes]}
clustering_results = {"STA/LTA" : "Earthquake", "Multi-window" : "Quake", "MER" : "Earthquake", "IMER" : "Rainfall", "TDER" : 'Quake'}

    # DIFFERENTES DONNEES AFFICHABLES
data_types = ["Raw trace", "Denoised trace", "STA/LTA", "Multi-window", "MER", "IMER", 'TDER']
selected = []






# 1ER ENCADRÉ (CHECKBOXES)

with st.container(height=110):
    st.markdown("**Displayed data :**")

        # On crée autant de colonnes que de données à afficher
    cols = st.columns(len(data_types))

    for i, type in enumerate(data_types):
        # On place chaque checkbox dans une colonne 
        if type == 'Denoised trace':
            cols[i].checkbox(type, key=type, value=True)
        else:
            cols[i].checkbox(type, key=type, value=False)


# pour qu'au départ la trace lissée apparaisse par défaut
if not selected and "Denoised trace" not in st.session_state:
    selected = ["Denoised trace"]


for type in data_types:
    if st.session_state.get(type, True):
        selected.append(type)



# Mise sous forme de DataFrame 
df = pd.DataFrame(data)
df['time'] = time
df['H1'] = h1
df['H2'] = h2
df['H3'] = h3
df['sta_lta_threshold'] = [st.session_state.sta_lta_threshold]*len(denoised_trace)
df['imer_threshold'] = [imer_threshold]*len(denoised_trace)
df['mer_threshold'] = [mer_threshold]*len(denoised_trace)
df['tder_threshold'] = [st.session_state.tder_threshold]*len(denoised_trace)


# couleurs
colors = {}

for i, type in enumerate(data_types):
    if i >= 4: 
        i += 1
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


    y1_max = max(data["Raw trace"]) if 'Raw trace' in selected else max(data['Denoised trace'])
    y2_max = 30
    fig.update_yaxes(range=[-y1_max, y1_max], secondary_y=False)
    fig.update_yaxes(range=[-y2_max, y2_max], secondary_y=True, dtick=y2_max)


    for type in data_types :

        if type in selected:

            is_secondary = type not in ['Raw trace', 'Denoised trace']
            
            if (not is_secondary) or (len(detection_times[type]) != 0): # si il y a bien une détection

                if type == "STA/LTA":

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df[type], 
                        name=f"{type} ratio",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='dash', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['sta_lta_threshold'], 
                        name=f"{type} threshold",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='solid', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )


                elif type == "Multi-window":

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df["R2"], 
                        name=f"{type} r2",
                        showlegend=True,
                        line=dict(dash='dot', color="#BEEC25"),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df["R3"], 
                        name=f"{type} r3",
                        showlegend=True,
                        line=dict(dash='dot', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=np.abs(analysed_trace), 
                        name=f"Absolute value of {st.session_state.trace_choice}",
                        showlegend=True,
                        line=dict(dash='dashdot', color=colors['Denoised trace']),
                        mode='lines'
                    ), secondary_y=False
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['H1'], 
                        name=f"{type} h1",
                        showlegend=True,
                        line=dict(dash='dashdot', color="#13EE9A"),
                        mode='lines'
                    ), secondary_y=False
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['H2'], 
                        name=f"{type} h2 & h3",
                        showlegend=True,
                        line=dict(dash='solid', color="#09D142"),
                        mode='lines'
                    ), secondary_y=True
                    )

                elif type == 'MER':
                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df[type], 
                        name=f"{type} ratio",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='dash', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['mer_threshold'], 
                        name=f"{type} threshold",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='solid', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )
                
                elif type == 'IMER':

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df[type], 
                        name=f"{type}",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='dash', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['imer_threshold'], 
                        name=f"{type} threshold",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='solid', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                elif type == 'TDER':

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df[type], 
                        name=f"{type}",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='dash', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
                    )

                    fig.add_trace(go.Scatter(
                        x=df["time"], 
                        y=df['tder_threshold'], 
                        name=f"{type} threshold",
                        legendgroup=type,
                        showlegend=True,
                        line=dict(dash='solid', color=colors[type]),
                        mode='lines'
                    ), secondary_y=True
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

                
            else:
                fig.add_trace(go.Scatter(
                    x=[df["time"].iloc[0]], 
                    y=[None], 
                    mode='lines', 
                    marker=dict(color=colors[type]),
                    name=f"{type} : No detection",
                    showlegend=True
                ), 
                )

                

    if 'Denoised trace' in selected or 'Raw trace' in selected:
        arrowsize = 30
        time_numeric = [t.timestamp() for t in time] # temps de la trace en format numérique pour numpy
        for method, list_events in detection_times.items():
            if len(detection_times[method]) == 0: # si pas de détection
                continue
            else:
                for i, x_event in enumerate(list_events):
                    x_event_numeric = x_event.timestamp() # x_event est un datetime, on le convertit en nombre pour le calcul
                    y_point = np.interp(x_event_numeric, time_numeric, analysed_trace)
                    fig.add_annotation(
                        x=x_event,
                        y=y_point,
                        text=f"{method} : {x_event.strftime('%H:%M:%S:%f')[:-4]}",
                        showarrow=True,
                        arrowhead=2,
                        arrowwidth=1,
                        arrowcolor= colors[method],
                        ax=0,
                        ay=arrowsize,
                        font=dict(color=colors[method], size=10),
                    )
                arrowsize += 15    

    fig.update_layout(title='Seismic trace through time', legend_title_text='<b>Legend :</b>', xaxis_title='Time', yaxis_title='Amplitude')
    fig.update_yaxes(range=[-y1_max, y1_max], title_text="<b>Amplitude</b> (Traces & h1)", secondary_y=False)
    fig.update_yaxes(range=[-y2_max, y2_max], title_text="<b>Amplitude</b> (Methods)", secondary_y=True, dtick=y2_max)

    st.plotly_chart(fig)






# 3EME ENCADRÉ (PARAMETRES)
with st.container(height=900):
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

    st.radio("Trace analysed :", ('Denoised trace', 'Raw trace'), horizontal=True, key='trace_choice')
    
    st.number_input('Wait time for new detection (s):', value=10, key='wait_time')

    for type in data_types:
        if type in detection_times.keys():
            st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> :", unsafe_allow_html=True) 
            with st.expander("Show parameters"):
                if type == "STA/LTA":
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.number_input('STA window length (s):', value=1, key='sta_duration_s')
                    with col2:
                        st.number_input('LTA window length (s):', value=10, key='lta_duration_s')
                    with col3:
                        st.number_input('STA/LTA threshold value :', value=4, key='sta_lta_threshold')

                if type == "Multi-window":
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.number_input('BTA window length (samples):', value=40, key='m')
                        st.number_input('Number of shifted samples (for H1) :', value=5, key='p')
                    with col2:
                        st.number_input('ATA window length (samples) :', value=30, key='n')
                        st.number_input('Average value of SNR :', value=3, key='average_snr')
                    with col3:
                        st.number_input('DTA window length (samples):', value=30, key='q')
                        st.number_input('Coefficient to adjust the height of H1 (α):', value=3, key='alpha')
                    with col4:
                        st.number_input('DTA delay (samples):', value=10, key='d')

                if type == "MER":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.number_input('Window length (ms) :', value=10, key='window_mer_ms')
                    with col2:
                        st.number_input('Threshold coefficient value :', value=0.67, key='threshold_mer_coeff')

                if type == "IMER":
                    st.radio("Low SNR :", (True, False), key='snr_bas', horizontal=True)
                    
                if type == "TDER":
                    col1, col2 = st.columns(2)
                    with col1:
                        st.number_input('Short window length (s) :', value=0.05, key='sw')
                    with col2:
                        st.number_input('Long window length (s) :', value=0.3, key='lw')
                    
    
                    





# 4EME ENCADRÉ (CLUSTERING)
    
with st.container(height=1700):
    st.markdown("**Clustering :**")
    
    clustering_files = [
        "../GUI_20230127_090749.mseed",
        "../RES_20230127_090749.mseed",
        "../GUI_20230103_090203.mseed",
        "../RES_20230103_090203.mseed",
        "../GUI_20230310_090649.mseed",
        "../RES_20230310_090649.mseed",
        "../GUI_20240112_095041.mseed",
        "../RES_20240112_095041.mseed",
        ]

    figs = []
    for file in clustering_files:
        data = lecture_mseed(file)
        trace = data[0]["data_samples"]
        fs = data[0]["sample_rate_hz"]
        start_str = data[0]["start_time"]
        start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        time = [start_dt + timedelta(seconds=i/fs) for i in range(len(trace))]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=time, y=trace, mode='lines'))
        if "GUI" in file:
            fig.update_layout(title=os.path.basename(file)+ " - capteur 1")
        else:
            fig.update_layout(title=os.path.basename(file)+ " - capteur 2")
        figs.append(fig)

    # Affichage en 2 colonnes de 3
    col1, col2 = st.columns(2)
    for i, fig in enumerate(figs):
        if i % 2 == 0:
            col1.plotly_chart(fig, use_container_width=True)
        else:
            col2.plotly_chart(fig, use_container_width=True)


    for type in data_types:
        if type in detection_times.keys():
            if len(detection_times[type]) == 0: # si pas de détection
                st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> : No detection", unsafe_allow_html=True)

            else:
                st.markdown(f"<span style='color:{colors[type]}; font-weight:bold;'>{type}</span> : {clustering_results[type]}", unsafe_allow_html=True)
