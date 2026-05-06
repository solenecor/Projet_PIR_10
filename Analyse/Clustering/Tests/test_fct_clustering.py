import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from fct_clustering_complet import *

if __name__ == "__main__" :
    k = 5

    series = lecture_initiale()

    start_time = time()
    G_visibility, m_visibility = clustering_visibility_graph(k, series)
    print("Graphe du clustering 1 construit")
    end_time = time()
    print(f"Temps de construction du graphe 1 : {end_time - start_time:.2f} secondes")
   
    start_time = time()
    G_L1, m_L1 = clustering_distance_L1(k, series)
    print("Graphe du clustering 2 construit")
    end_time = time()
    print(f"Temps de construction du graphe 2 : {end_time - start_time:.2f} secondes")

    start_time = time()
    G_L2, m_L2 = clustering_distance_L2(k, series)
    print("Graphe du clustering 3 construit")
    end_time = time()
    print(f"Temps de construction du graphe 3 : {end_time - start_time:.2f} secondes")
    
    start_time = time()
    G_dtw, m_dtw = clustering_distance_dtw(k, series)
    print("Graphe du clustering 4 construit")
    end_time = time()
    print(f"Temps de construction du graphe 4 : {end_time - start_time:.2f} secondes")

    plt.figure(1)
    pos = nx.spring_layout(G_visibility, weight='weight')
    nx.draw_networkx(G_visibility, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_visibility, 'weight').items()}
    nx.draw_networkx_edge_labels(G_visibility, pos, edge_labels=edge_labels)


    plt.figure(2)
    pos = nx.spring_layout(G_L1, weight='weight')
    nx.draw_networkx(G_L1, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_L1, 'weight').items()}
    nx.draw_networkx_edge_labels(G_L1, pos, edge_labels=edge_labels)

    plt.figure(3)
    pos = nx.spring_layout(G_L2, weight='weight')
    nx.draw_networkx(G_L2, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_L2, 'weight').items()}
    nx.draw_networkx_edge_labels(G_L2, pos, edge_labels=edge_labels)


    plt.figure(4)
    pos = nx.spring_layout(G_dtw, weight='weight')
    nx.draw_networkx(G_dtw, pos, with_labels=True)
    edge_labels = {k: round(v, 3) for k, v in nx.get_edge_attributes(G_dtw, 'weight').items()}
    nx.draw_networkx_edge_labels(G_dtw, pos, edge_labels=edge_labels)

    plt.show()


    ### Comparaison de la similarité si on a que 2 séries:
    
    """print(f"Similarité ac visibility graph : {G_visibility.edges[0,1]['weight']}")
    print(f"Similarité ac DTW : {G_dtw.edges[0,1]['weight']}")
    print(f"Similarité ac L1 : {G_L1.edges[0,1]['weight']}")
    print(f"Similarité ac L2 : {G_L2.edges[0,1]['weight']}")"""