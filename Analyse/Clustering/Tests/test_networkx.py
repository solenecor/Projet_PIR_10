from networkx import * 
import pylab as P


G = Graph()
G.add_node(0)
G.add_nodes_from([2,3])
G.add_node(4)
G.add_edges_from([(0,2),(0,3),(2,4),(3,4)])


draw(G)
P.show()
draw_circular(G)