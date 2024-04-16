import networkx as nx
import matplotlib.pyplot as plt
import itertools
import os
from tqdm import tqdm
import copy
import pickle


class Graph:

  def __init__(self, node_count):
    self.nodes = [set() for _ in range(node_count)]
    self.back_nodes = [set() for _ in range(node_count)]
    self.edge_count = 0

  def add_edge(self, i, j):
    if i != j:
      if j in self.nodes[i]:
        self.nodes[i].remove(j)
        self.back_nodes[j].remove(i)
        self.nodes[j].add(i)
        self.back_nodes[i].add(j)
      elif i in self.nodes[j]:
        self.nodes[j].remove(i)
        self.back_nodes[i].remove(j)
        self.edge_count -= 1
      else:
        self.nodes[i].add(j)
        self.back_nodes[j].add(i)
        self.edge_count += 1

  def to_nx_graph(self):
    gr = nx.DiGraph()
    gr.add_nodes_from(list(range(len(self.nodes))))
    for node, endpoints in enumerate(self.nodes):
      for node2 in endpoints:
        gr.add_edge(node, node2)
    return gr

  def hash(self):
    return nx.weisfeiler_lehman_graph_hash(self.to_nx_graph())


def apply_permutation(gr, pr):
  node_count = len(gr.nodes)
  new_gr = Graph(node_count)
  for node in range(node_count):
    for node2 in gr.nodes[node]:
      new_gr.add_edge(pr[node], pr[node2])
  return new_gr


def generate_all_permutations(n):
  return list(itertools.permutations(list(range(n))))


def are_isomorphic(gr1, gr2):
  if len(gr1.nodes) != len(gr2.nodes) or gr1.edge_count != gr2.edge_count:
    return False
  node_count = len(gr1.nodes)
  all_prs = generate_all_permutations(node_count)
  for pr in all_prs:
    if apply_permutation(gr1, pr).nodes == gr2.nodes:
      return True
  return False


def have_same_h(gr1, gr2):
  return gr1.hash() == gr2.hash()


def gen(node_count):

  combinations = list(itertools.product([0, 1, 2], repeat=node_count*(node_count-1)//2))
  edges = [(i, j) for i in range(node_count) for j in range(i+1, node_count)]
  graphs = []
  graph_hashes = {}
  for combo in tqdm(combinations):
    graph = Graph(node_count)
    for i, arrow in enumerate(combo):
      if arrow == 1:
        graph.add_edge(*edges[i])
      elif arrow == 2:
        graph.add_edge(edges[i][1], edges[i][0])
    graph_h = graph.hash()
    if graphs:
      if graph_h not in graph_hashes:
        graphs.append(graph)
        graph_hashes[graph_h] = [graph]
      else:
        for gr in graph_hashes[graph_h]:
          if are_isomorphic(gr, graph):
            break
        else:
          graphs.append(graph)
          graph_hashes[graph_h].append(graph)
      # for gr in graphs:
      #   if are_isomorphic(gr, graph):
      #     break
      # else:
      #   graphs.append(graph)
    else:
      graphs.append(graph)
      graph_hashes[graph_h] = [graph]
  return graphs


def transform1(graph, node1, node2):
  graph_copy = copy.deepcopy(graph)
  for back_node in graph_copy.back_nodes[node1]:
    graph_copy.add_edge(back_node, node2)
  for next_node in graph_copy.nodes[node1]:
    graph_copy.add_edge(node2, next_node)
  return graph_copy


def transform2(graph, node):
  graph_copy = copy.deepcopy(graph)
  back_nodes = graph_copy.back_nodes[node].copy()
  next_nodes = graph_copy.nodes[node].copy()
  for back_node in back_nodes:
    graph_copy.add_edge(node, back_node)
    graph_copy.add_edge(node, back_node)
  for next_node in next_nodes:
    graph_copy.add_edge(next_node, node)
    graph_copy.add_edge(next_node, node)
  return graph_copy


def create_source_graphs(node_count):
  upper_point = (node_count+1) if node_count % 2 == 0 else node_count
  source_graphs = [Graph(node_count)]
  for m in range(2, upper_point, 2):
    gr = Graph(node_count)
    for i in range(0, m, 2):
      gr.add_edge(i, i+1)
    source_graphs.append(gr)
  return source_graphs


def get_all_inclass_graphs(source_graph, node_count):
  duos = [(i, j) for i in range(node_count) for j in range(node_count) if i != j]
  queue = [source_graph]
  hashes = {source_graph.hash(): [source_graph]}
  graphs = [source_graph]
  while queue:
    gr = queue[0]
    queue.pop(0)
    for node1, node2 in duos:
      new_gr = transform1(gr, node1, node2)
      new_gr_h = new_gr.hash()
      if new_gr_h not in hashes:
        queue.append(new_gr)
        hashes[new_gr_h] = [new_gr]
        graphs.append(new_gr)
      # else:
      #   for gr in hashes[new_gr_h]:
      #     if are_isomorphic(gr, new_gr):
      #       break
      #   else:
      #     queue.append(new_gr)
      #     hashes[new_gr_h].append(new_gr)
      #     graphs.append(new_gr)

    for node in range(node_count):
      new_gr = transform2(gr, node)
      new_gr_h = new_gr.hash()
      if new_gr_h not in hashes:
        queue.append(new_gr)
        hashes[new_gr_h] = [new_gr]
        graphs.append(new_gr)
      # else:
      #   for gr in hashes[new_gr_h]:
      #     if are_isomorphic(gr, new_gr):
      #       break
      #   else:
      #     queue.append(new_gr)
      #     hashes[new_gr_h].append(new_gr)
      #     graphs.append(new_gr)
  return graphs, hashes


def main(node_count):
  all_graphs = gen(node_count)
  source_graphs = create_source_graphs(node_count)
  overall_gr_count = 0
  fusion_classes = []
  for s_gr in source_graphs:
    inclass_graphs, inclass_hashes = get_all_inclass_graphs(s_gr, node_count)
    print(len(inclass_graphs))
    overall_gr_count += len(inclass_graphs)
    fusion_classes.append(inclass_graphs)
  print(len(all_graphs), overall_gr_count)
  return fusion_classes


if __name__ == "__main__":
    fusion_classes = main(6)
    # with open("fusion_classes.pkl", 'wb') as outp:
    #     pickle.dump(fusion_classes, outp, pickle.HIGHEST_PROTOCOL)
