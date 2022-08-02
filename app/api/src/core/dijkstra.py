from collections import defaultdict, deque

import numpy as np


class Dijkstra:
    def generate_adjacancy_list(self, data_edges):
        self.adjacancy_list = defaultdict(set)
        for edge in data_edges.itertuples():
            self.adjacancy_list[edge.source].add((edge.target, edge.cost))
            self.adjacancy_list[edge.target].add((edge.source, edge.reverse_cost))

    def calculate_target_costs(self, node_id, calculator_id):
        """
        Calculate costs for adjacent vertexes
        """
        # targets = coo_matrix(self.sparse_graph.getrow(node_id))
        self.unvisited_vertexes.remove(node_id)
        for target_id, cost in self.adjacancy_list[node_id]:
            distance = self.distances[node_id] + cost
            if distance < self.distances[target_id]:
                self.distances[target_id] = distance
                self.calculator[target_id] = calculator_id
                self.to_visit.append(target_id)

            elif self.calculator[target_id] < calculator_id:
                print("calculator skip trigered.")
                if target_id in self.unvisited_vertexes:
                    self.unvisited_vertexes.remove(target_id)

    def dijkstra(self):
        """
        Calculate distances with walking through Graph WITHOUT recursive function
        """
        calculator_id = 0
        for start_vertex in self.start_vertexes:

            calculator_id += 1
            self.unvisited_vertexes = self.vertexes_set
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
        self.distance_limit = max(distance_limit) * 60
        self.distances = {}
        self.calculator = {}
        self.generate_adjacancy_list(data_edges)
        self.vertexes_set = set(self.adjacancy_list.keys())
        for vertex in self.vertexes_set:
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