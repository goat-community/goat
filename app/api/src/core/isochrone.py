import numpy as np
from scipy import sparse

# class Mapping(dict):
#     """
#     Return key of founded value.
#     Ref: https://stackoverflow.com/a/8023337/1951027
#     """

#     def find_value(self, search_value):
#         for key, value in self.items():
#             if value == search_value:
#                 return value
#         return None

#     def find_key(self, search_key):
#         for key, value in self.items():
#             if key == search_key:
#                 return key
#         return None


class Isochrone:
    # def remap_edges(self):
    #     mapping = Mapping()
    #     for edge in self.data_edges:
    #         it = mapping.find_value(edge["source"])

    #         if it:
    #             source_id = it
    #         else:
    #             id += 1
    #             source_id = id
    #             mapping[edge["source"]] = source_id

    #         it = mapping.find_value(edge["target"])
    #         if it:
    #             target_id = it
    #         else:
    #             id += 1
    #             target_id = id
    #             mapping[edge["target"]] = target_id

    #         edge["source"] = source_id
    #         edge["target"] = target_id
    #     self.mapping = mapping
    #     return mapping

    # def construct_adjustancy_list(self):
    #     adj = [[]]
    #     for edge in self.data_edges:
    #         if edge["cost"] >= 0:
    #             adj[edge["source"]].append(edge)

    #         if edge["reverse_cost"] >= 0:
    #             adj[edge["target"]].append(edge)

    #     return adj

    def build_sparse_costs(self):
        row = np.concatenate([self.data_edges["source"], self.data_edges["target"]])
        col = np.concatenate([self.data_edges["target"], self.data_edges["source"]])
        costs = np.concatenate([self.data_edges["costs"], self.data_edges["reverse_costs"]])
        self.sparse_matrix = sparse.coo_matrix((costs, (row, col)), dtype=np.double)

    def dijkstra_(self, indice, distance_limit):
        dijkstra = sparse.csgraph.dijkstra(
            self.sparse_matrix, indices=[indice], limit=distance_limit
        )
        return dijkstra

    def do_dijkstra(self):
        self.build_sparse_costs()
        self.distances_list = []
        self.predecessors_list = []
        for indice, distance_limit in zip(self.start_vertecies, self.distance_limits):
            distances, predecessors = self.dijkstra_(indice, distance_limit)
            self.distances_list.append(distances)
            self.predecessors_list.append(predecessors)

    def compute_isochrone(self):
        # mapping = self.remap_edges()
        # coordinates = Mapping()
        # nodes_count = len(mapping)

        self.do_dijkstra()

    def __init__(
        self, data_edges, start_vertecies, distance_limits, only_minimum_cover=False
    ) -> None:
        self.data_edges = data_edges
        self.start_vertecies = start_vertecies
        self.distance_limits = distance_limits
        self.only_minimum_cover = only_minimum_cover
