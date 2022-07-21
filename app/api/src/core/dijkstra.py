from collections import deque

import numpy as np
from scipy.sparse import coo_matrix, csr_matrix


class Dijkstra:
    def generate_sparse_graph(self):
        """
        Generate Sparse Graph of edges and their costs (sources, targets, costs)
        """
        data_edges = self.data_edges
        row = np.concatenate([data_edges["source"], data_edges["target"]])
        col = np.concatenate([data_edges["target"], data_edges["source"]])
        cost_data = np.concatenate([data_edges["cost"], data_edges["reverse_cost"]])
        sparse_graph = csr_matrix((cost_data, (row, col)), dtype=np.double)
        unvisited_vertexes = set(row)
        return sparse_graph, unvisited_vertexes

    def calculate_target_costs(self, node_id, calculator_id):
        """
        Calculate costs for adjacent vertexes
        """
        targets = coo_matrix(self.sparse_graph.getrow(node_id))
        self.unvisited_vertexes.remove(node_id)
        for cost, target_id in zip(targets.data, targets.col):
            distance = self.distances[node_id] + cost
            if distance < self.distances[target_id]:
                self.distances[target_id] = distance
                self.calculator[target_id] = calculator_id
                self.to_visit.append(target_id)
            else:
                if self.calculator[target_id] < calculator_id:
                    if target_id in self.unvisited_vertexes:
                        self.unvisited_vertexes.remove(target_id)

    def dijkstra(self):
        """
        Calculate distances with walking through Graph WITHOUT recursive function
        """
        calculator_id = 0
        for start_vertex in self.start_vertexes:

            calculator_id += 1
            self.unvisited_vertexes = self.unique_vertexes
            self.to_visit = deque([start_vertex])
            self.distances[start_vertex] = 0
            while self.to_visit:
                node_id = self.to_visit.popleft()
                if node_id in self.unvisited_vertexes:
                    if self.distances[node_id] < self.distance_limit:
                        self.calculate_target_costs(node_id, calculator_id)
                    else:
                        self.unvisited_vertexes.remove(node_id)

        return self.distances

    def __init__(self, data_edges, start_vertexes, distance_limit):
        self.data_edges = data_edges
        self.start_vertexes = start_vertexes
        self.distance_limit = distance_limit
        self.distances = {}
        self.calculator = {}
        self.sparse_graph, self.unique_vertexes = self.generate_sparse_graph()
        for vertex in self.unique_vertexes:
            self.distances[vertex] = np.inf
            self.calculator[vertex] = np.inf


def dijkstra(data_edges, start_vertexes, distance_limit):
    d = Dijkstra(data_edges, start_vertexes, distance_limit)
    return d.dijkstra()


if __name__ == "__main__":
    from src.tests.utils.isochrone import get_sample_network

    edges_network, starting_id, distance_limits = get_sample_network(minutes=5)
    distances = dijkstra(edges_network, starting_id, distance_limits[0])
    print()
