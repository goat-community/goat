import math

import matplotlib.pyplot as plt
import numpy as np
import pyproj
from scipy.interpolate import LinearNDInterpolator
from shapely.geometry import Point
from shapely.ops import transform

from src.core.dijkstra import Dijkstra
from src.utils import coordinate_to_pixel


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

    def get_north_west(self, x, y, zoom):
        project = pyproj.Transformer.from_crs(
            pyproj.CRS("EPSG:3857"), pyproj.CRS("EPSG:4326"), always_xy=True
        ).transform
        point = Point(x.min(), y.max())
        lon_lat_point = transform(project, point)
        point_pixel = coordinate_to_pixel([lon_lat_point.x, lon_lat_point.y], zoom=zoom)
        x_ = math.floor(point_pixel["x"])
        y_ = math.floor(point_pixel["y"])
        return y_, x_

    def build_grid_interpolate(self, zoom):
        points = self.points.transpose()
        min_x = math.floor(points[0].min())
        min_y = math.floor(points[1].min())
        max_x = math.ceil(points[0].max())
        max_y = math.ceil(points[1].max())
        self.X = np.arange(start=min_x, stop=max_x, step=20)
        self.Y = np.arange(start=min_y, stop=max_y, step=20)
        self.X, self.Y = np.meshgrid(self.X, self.Y)  # 2D grid for interpolation
        x = points[0]
        y = points[1]
        z = self.costs
        interpolate_function = LinearNDInterpolator(list(zip(x, y)), z)
        self.Z = interpolate_function(self.X, self.Y)

        return self.X, self.Y, self.Z

    def compute_isochrone(self, zoom):
        self.dijkstra()
        self.get_isochrone_network()
        self.build_grid_interpolate(zoom)

    def plot(self):
        plt.pcolormesh(self.X, self.Y, self.Z, shading="nearest")
        plt.legend()
        plt.colorbar()
        plt.axis("equal")
        plt.savefig("LinearNDInterpolator.png")

    def get_single_depth_grid(self, zoom):
        grid_type = "ACCESSGR"
        north, west = self.get_north_west(self.X, self.Y, zoom)
        grid_data = {}
        Z = np.ravel(self.Z)
        Z = np.nan_to_num(Z, nan=np.iinfo(np.intc).max)
        Z[Z < 1000] = 10  # This should go to jsoline
        grid_data["version"] = 0
        grid_data["zoom"] = zoom
        grid_data["west"] = west
        grid_data["north"] = north
        grid_data["width"] = self.Z.shape[0]
        grid_data["height"] = self.Z.shape[1]
        grid_data["depth"] = 1
        grid_data["data"] = Z

        return grid_data


def isochrone_single_depth_grid(data_edges, start_vertexes, distance_limit, zoom: int = 10):
    isochrone = Isochrone(data_edges, start_vertexes, distance_limit)
    isochrone.compute_isochrone(zoom)
    return isochrone.get_single_depth_grid(zoom)


if __name__ == "__main__":
    from src.tests.utils.isochrone import get_sample_network

    edges_network, starting_id, distance_limits = get_sample_network(minutes=4)
    isochrone = Isochrone(edges_network, starting_id, distance_limits)
    isochrone.compute_isochrone(10)
    a = isochrone.get_single_depth_grid(10)
    isochrone.plot()

    print()
