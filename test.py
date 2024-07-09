import networkx as nx
import matplotlib.pyplot as plt

def create_graph():
    graph = nx.Graph()
    graph.add_nodes_from(['a', 'b', 'c', 'd', 'e', 'f'])
    graph.add_edges_from([
        ('a', 'b'), ('a', 'c'), ('b', 'e'), 
        ('b', 'd'), ('c', 'f'), ('a', 'f')
    ])
    return graph

def find_paths(graph, source, target):
    if source not in graph or target not in graph:
        print("Uno o ambos nodos no existen en el grafo.")
        return
    print(f'Todos los caminos posibles de nodo {source} para nodo {target}:')
    for path in nx.all_simple_paths(graph, source, target):
        print(path)

def main():
    graph = create_graph()
    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()
    source = input('Enter the source node >> ')
    target = input('Enter the target node >> ')
    find_paths(graph, source, target)

if __name__ == "__main__":
    main()