import pickle
import networkx as nx
import matplotlib.pyplot as plt
import itertools
import os
from tqdm import tqdm
import copy

from main import Graph

def to_nx_graphs(graphs):
  return [graph.to_nx_graph() for graph in graphs]

def vis_graphs(graphs):
  graphs = to_nx_graphs(graphs)
  num_graphs = len(graphs)
  fig, axs = plt.subplots(1, num_graphs, figsize=(10*num_graphs, 10))

  for i, graph in enumerate(graphs):
      nx.draw(graph, ax=axs[i], with_labels=True, node_color='lightblue', node_size=500, arrowsize=40)
      axs[i].set_title(f"Graph {i+1}")

  plt.tight_layout()
  plt.show()


def testing():
    with open('fusion_classes_old.pkl', 'rb') as inp:
        fusion_classes = pickle.load(inp)

    fusion_hashes = []
    for cl in fusion_classes:
        cl_hashes = set()
        for gr in cl:
            cl_hashes.add(gr.hash())
        fusion_hashes.append(cl_hashes)

    h = '063824182038d29f1e0251a14e88bf1e'

    for gr in fusion_classes[0]:
        if gr.hash() == h:
            gr1 = gr
            break

    for gr in fusion_classes[1]:
        if gr.hash() == h:
            gr2 = gr
            break

    vis_graphs([gr1, gr2])

    # print(fusion_hashes[0] & fusion_hashes[1])
    #
    # print(len(fusion_hashes[0] & fusion_hashes[2]))
    # print(len(fusion_hashes[2] & fusion_hashes[1]))
    #
    # gr = Graph(6)
    # gr.add_edge(0, 1)
    #
    # print(gr.hash())


if __name__ == "__main__":
    testing()
