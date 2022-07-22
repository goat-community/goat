import math

import matplotlib.pyplot as plt
import numpy as np
from dijkstra import Dijkstra
from scipy.interpolate import LinearNDInterpolator, NearestNDInterpolator


class Isochrone(Dijkstra):
    def get_isochrone_network(self):
        point_ids = set(self.distances.keys())
        for id in list(point_ids):
            if np.isinf(self.distances[id]):
                point_ids.remove(id)
        points = []
        costs = [self.distances[id] for id in point_ids]

        for point in point_ids:
            found_point = np.where(self.data_edges["source"] == point)
            if len(found_point[0]):
                found_point = found_point[0][0]
                points.append(self.data_edges["geom"][found_point][0])
            else:
                found_point = np.where(self.data_edges["target"] == point)
                if len(found_point[0]):
                    found_point = found_point[0][0]
                    points.append(self.data_edges["geom"][found_point][-1])

        """
        points is like: {234234: [23.3423424,22.23423423]}
        """
        self.points = np.array(points, dtype=np.double)
        self.costs = np.array(costs, dtype=np.double)

    def build_grid_interpolate(self):
        points = self.points.transpose()
        min_x = math.floor(points[0].min())
        min_y = math.floor(points[1].min())
        max_x = math.ceil(points[0].max())
        max_y = math.ceil(points[1].max())
        X = np.arange(start=min_x, stop=max_x, step=20)
        Y = np.arange(start=min_y, stop=max_y, step=20)
        X, Y = np.meshgrid(X, Y)  # 2D grid for interpolation
        x = points[0]
        y = points[1]
        z = self.costs
        interpolate_function = LinearNDInterpolator(list(zip(x, y)), z)
        Z = interpolate_function(X, Y)
        return X, Y, Z
        # plt.pcolormesh(X, Y, Z, shading="nearest")
        # plt.legend()
        # plt.colorbar()
        # plt.axis("equal")
        # plt.savefig("LinearNDInterpolator.png")

    def compute_isochrone(self):
        self.dijkstra()
        self.get_isochrone_network()
        self.build_grid_interpolate()
        pass


if __name__ == "__main__":
    from src.tests.utils.isochrone import get_sample_network

    edges_network, starting_id, distance_limits = get_sample_network(minutes=4)
    isochrone = Isochrone(edges_network, starting_id, distance_limits[0])
    isochrone.compute_isochrone()

    print()
