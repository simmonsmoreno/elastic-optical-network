import networkx as nx
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, Text, END

def create_graph():
    graph = nx.Graph()
    graph.add_nodes_from(['a', 'b', 'c', 'd', 'e', 'f'])
    graph.add_edges_from([
        ('a', 'b'), ('a', 'c'), ('b', 'e'), 
        ('b', 'd'), ('c', 'f'), ('a', 'f')
    ])
    return graph

def find_paths(graph, source, target, output_text):
    output_text.delete('1.0', END)  # Limpa a caixa de texto antes de mostrar novos caminhos
    if source not in graph or target not in graph:
        output_text.insert(END, "Uno o ambos nodos no existen en el grafo.\n")
        return
    output_text.insert(END, f'Todos los caminos posibles de nodo {source} para nodo {target}:\n')
    for path in nx.all_simple_paths(graph, source, target):
        output_text.insert(END, f'{path}\n')

def main():
    graph = create_graph()
    nx.draw(graph, with_labels=True, font_weight='bold')
    plt.show()
    
    # GUI
    window = Tk()
    window.title("Path Finder in Graph")
    
    Label(window, text="Enter the source node:").grid(row=0, column=0)
    source_entry = Entry(window)
    source_entry.grid(row=0, column=1)
    
    Label(window, text="Enter the target node:").grid(row=1, column=0)
    target_entry = Entry(window)
    target_entry.grid(row=1, column=1)
    
    output_text = Text(window, height=10, width=50)
    output_text.grid(row=3, column=0, columnspan=2)
    
    find_button = Button(window, text="Find Paths", command=lambda: find_paths(graph, source_entry.get(), target_entry.get(), output_text))
    find_button.grid(row=2, column=0, columnspan=2)
    
    window.mainloop()

if __name__ == "__main__":
    main()