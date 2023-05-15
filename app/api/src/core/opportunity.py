from collections import defaultdict
import os
import numpy as np
import pandas as pd
from geopandas import GeoDataFrame, clip, read_parquet, read_postgis
from pandas import concat
from shapely.geometry import box
from shapely.wkt import loads as wkt_loads

from src.core.config import settings
from src.db.session import legacy_engine
from src.utils import create_h3_grid


class Opportunity:
    """
    Reads opportunity data from parquet files or database.
    """

    def __init__(self):
        layers = {
            "poi": ["uid", "category", "geometry"],
            "population": ["population", "building_id", "geometry"],
            "population_grouped": ["population", "building_id", "geometry"],
            "aoi": ["id", "geometry"],
        }
        self.layers = layers
        self.layers_modifiable = ["poi", "population"]
        self.layers_user_data = ["poi"]

    def read_h3_parquet(
        self, layer: str, h3_indexes: list, type: str = "original", s3_folder: str = ""
    ) -> GeoDataFrame:
        """
        Read parquet files.

        :param layer: The layer name.
        :param h3_indexes: The h3 indexes.
        :param type: The type of data (original or grid (aggregated)).
        :param s3_folder: The s3 folder (Optional).

        :return: A GeoDataFrame with the data.
        """
        if layer not in self.layers:
            raise ValueError(f"Layer {layer} not in {self.layers.keys()}.")

        layer_gdfs = []
        for h3_index in h3_indexes:
            try:
                dir_name = f"{settings.OPPORTUNITY_PATH}/{type}/{h3_index}"
                file_path = f"{dir_name}/{layer}.parquet"
                if s3_folder != "" and not os.path.exists(file_path):
                    print(f"File {file_path} not found. Trying to download from S3.")
                    if not os.path.exists(dir_name):
                        os.makedirs(dir_name, exist_ok=True)
                    s3_path = f"{s3_folder}/opportunity/{type}/{h3_index}/{layer}.parquet"
                    settings.S3_CLIENT.download_file(settings.AWS_BUCKET_NAME, s3_path, file_path)

                layer_gdf = read_parquet(file_path)
                layer_gdfs.append(layer_gdf)
            except Exception as e:
                print(e)

        return layer_gdfs

    def read_base_data(
        self,
        layer: str,
        h3_indexes: list,
        bbox_wkt: str = None,
        type: str = "original",
        s3_folder="",
    ) -> GeoDataFrame:
        """
        Read base data.

        :param layer: The layer name.
        :param h3_indexes: The h3 indexes.
        :param bbox_wkt: The bounding box (Optional).
        :param type: The type of data (original or grid (aggregated)).
        :param s3_folder: The s3 folder (Optional).

        :return: A GeoDataFrame with the data.
        """

        layer_gdf = self.read_h3_parquet(layer, h3_indexes, type=type, s3_folder=s3_folder)

        if len(layer_gdf) > 0:
            layer_gdf = concat(layer_gdf, ignore_index=True)
        else:
            # If there is no data, return an empty GeoDataFrame.
            layer_gdf = GeoDataFrame(columns=self.layers[layer], crs="EPSG:4326")

        if bbox_wkt is not None and len(layer_gdf) > 0:
            layer_gdf = clip(layer_gdf, wkt_loads(bbox_wkt))

        return layer_gdf

    def read_modified_data(
        self,
        db,
        layer: str,
        scenario_id: int,
        bbox_wkt: str = None,
        edit_type: list = ["n", "m", "d"],
    ) -> GeoDataFrame:
        """
        Read modified data.

        :param layer: The layer name.
        :param scenario_id: The scenario id.
        :param bbox_wkt: The bounding box (Optional).
        :param edit_type: The edit type (n: new, m: modified, d: deleted).

        :return: A GeoDataFrame with the data.
        """
        if scenario_id == 0:
            return None

        if layer not in self.layers_modifiable:
            raise ValueError(f"Layer {layer} not in modifiable layers {self.layers_modifiable}.")

        sql_query = (
            f"""SELECT * FROM customer.{layer}_modified p WHERE p.scenario_id = {scenario_id} """
        )

        if layer == "poi":
            sql_query += f""" AND p.edit_type IN (SELECT UNNEST(ARRAY{edit_type}::text[]))"""

        if bbox_wkt is not None:
            sql_query += f""" AND ST_Intersects('SRID=4326;{bbox_wkt}'::geometry, p.geom)"""

        modified_gdf = read_postgis(
            sql_query,
            db,
            crs="EPSG:4326",
        )

        if len(modified_gdf) == 0:
            # If there is no data, return None to avoid warnings on crs when merging.
            modified_gdf = None

        return modified_gdf

    def read_user_data(
        self, db, layer: str, user_active_upload_ids: list[int], bbox_wkt: str = None
    ) -> GeoDataFrame:
        """
        Read user data.

        :param layer: The layer name.

        :return: A GeoDataFrame with the data.
        """
        if len(user_active_upload_ids) == 0:
            return None

        if layer not in self.layers_user_data:
            raise ValueError(f"Layer {layer} not in user data layers {self.layers_user_data}.")

        sql_query = f"""SELECT * FROM customer.{layer}_user p WHERE p.data_upload_id IN (SELECT UNNEST(ARRAY{user_active_upload_ids}::integer[]))"""
        if bbox_wkt is not None:
            sql_query += f""" AND ST_Intersects('SRID=4326;{bbox_wkt}'::geometry, p.geom)"""

        user_gdf = read_postgis(
            sql_query,
            db,
            crs="EPSG:4326",
        )

        if len(user_gdf) == 0:
            # If there is no data, return None to avoid warnings on crs when merging.
            user_gdf = None

        return user_gdf

    def read_poi(
        self,
        db,
        h3_indexes: list,
        user_id: int,
        scenario_id: int,
        user_active_upload_ids: list[int],
        bbox_wkt: str = None,
    ) -> GeoDataFrame:
        """
        Read poi data.

        :param h3_indexes: The h3 indexes.
        :param scenario_id: The scenario id.
        :param user_active_upload_ids: The user active upload ids.
        :param bbox_wkt: The bounding box wkt.

        :return: A GeoDataFrame with the data.
        """
        # - Excluded features that are modified by the user.
        # Returns list of poi uid [1k3uirdsd, 2k3uirdsd, 3k3uirdsd] of features that are modified.
        modified_poi_uids = []
        if scenario_id != 0:
            modified_poi_uids = pd.read_sql(
                f"SELECT * FROM basic.modified_pois({scenario_id})",
                db,
            ).iloc[0][0]
        # - Get the poi categories for one entrance and multiple entrances.
        # Returns {'true': [restaurant, shop...], 'false': [bus_stop, train_station...]}
        poi_categories = pd.read_sql(
            f"SELECT * FROM basic.poi_categories({user_id})",
            db,
        ).iloc[
            0
        ][0]
        poi_multiple_entrances = poi_categories["true"]

        poi_gdf = self.read_base_data("poi", h3_indexes)
        poi_user_gdf = self.read_user_data(db, "poi", user_active_upload_ids, bbox_wkt)
        poi_gdf = concat([poi_gdf, poi_user_gdf], ignore_index=True)
        if len(modified_poi_uids) > 0:
            # this will filter out "deleted" and "modified" features from the base data
            poi_gdf = poi_gdf[~poi_gdf["uid"].isin(modified_poi_uids)]

        poi_modified_gdf = self.read_modified_data(db, "poi", scenario_id, bbox_wkt)
        poi_gdf = concat([poi_gdf, poi_modified_gdf], ignore_index=True)

        # add entrance type as columns
        poi_gdf["entrance_type"] = np.where(
            poi_gdf["category"].isin(poi_multiple_entrances), "multiple", "one"
        )

        return poi_gdf

    def read_population(
        self,
        db,
        h3_indexes: list,
        scenario_id: int,
        bbox_wkt: str = None,
    ) -> GeoDataFrame:
        """
        Read population data.

        :param h3_indexes: The h3 indexes.
        :param scenario_id: The scenario id.
        :param user_active_upload_ids: The user active upload ids.
        :param bbox_wkt: The bounding box wkt.

        :return: A GeoDataFrame with the data.
        """
        # - Excluded features that are modified by the user.
        # Returns list of populationv uid [1k3uirdsd, 2k3uirdsd, 3k3uirdsd] of features that are modified.
        modified_buildings = []
        if scenario_id != 0:
            modified_buildings = pd.read_sql(
                f"SELECT * FROM basic.modified_buildings({scenario_id})",
                legacy_engine,
            ).iloc[0][0]

        # - Read population data.
        population_gdf = self.read_base_data("population", h3_indexes)
        if len(modified_buildings) > 0:
            # this will filter out "deleted" and "modified" features from the base data
            population_gdf = population_gdf[
                ~population_gdf["building_id"].isin(modified_buildings)
            ]

        population_modified_gdf = self.read_modified_data(db, "population", scenario_id, bbox_wkt)

        population_gdf = concat([population_gdf, population_modified_gdf], ignore_index=True)

        return population_gdf

    def read_aoi(
        self,
        h3_indexes: list,
    ) -> GeoDataFrame:
        """
        Read aoi data.

        :param h3_indexes: The h3 indexes.

        :return: A GeoDataFrame with the data.
        """
        # No modifications or user uploaded data to aoi data.
        aoi_gdf = self.read_base_data("aoi", h3_indexes)
        return aoi_gdf


class OpportunityIntersect(Opportunity):
    def __init__(
        self,
        input_geometries: GeoDataFrame,
        user_id: int = 0,
        user_active_upload_ids: list = [],
        scenario_id: int = 0,
        hexagon_size: int = 6,
    ):
        """Intersect opportunity data with geometries.

        Args:
            input_geometries (GeoDataFrame): Geometries to intersect with opportunity data.
            user_id (int, optional): The user id. Defaults to 0.
            user_active_upload_ids (list, optional): The user active upload ids. Defaults to [].
            scenario_id (int, optional): The user scenario id. Defaults to 0.
            hexagon_size (int, optional): The hexagon size of parque tiles. Defaults to 6.
        """
        Opportunity.__init__(self)
        self.input_geometries = input_geometries
        self.user_id = user_id
        self.user_active_upload_ids = user_active_upload_ids
        self.scenario_id = scenario_id
        geometry_bounds = input_geometries["geometry"][
            ~input_geometries["geometry"].is_empty
        ].apply(lambda geom: box(*geom.bounds, ccw=True))
        bbox = geometry_bounds.unary_union
        self.bbox_wkt = bbox.wkt
        self.h3_grid_gdf = create_h3_grid(bbox, hexagon_size, intersect_with_centroid=False)

    def poi(self):
        """
        Count the number of opportunities for each cutoff.

        :param group_by: The input_geometries column to group by.

        :return: A dictionary with the cummulative number of opportunities for each cutoff.

        """
        poi_gdf = self.read_poi(
            legacy_engine,
            self.h3_grid_gdf["h3_index"].tolist(),
            self.user_id,
            self.scenario_id,
            self.user_active_upload_ids,
            self.bbox_wkt,
        )

        poi_gdf_join = self.input_geometries.sjoin(poi_gdf, predicate="intersects", how="inner")

        return poi_gdf_join

    def population(self) -> GeoDataFrame:
        """
        Intersect the population for each cutoff.

        :return: A GeoDataFrame of population for each cutoff.

        """
        population_gdf = self.read_population(
            legacy_engine,
            self.h3_grid_gdf["h3_index"],
            self.scenario_id,
            self.bbox_wkt,
        )

        population_gdf_join = self.input_geometries.sjoin(
            population_gdf, predicate="intersects", how="inner"
        )

        return population_gdf_join

    def aoi(self) -> GeoDataFrame:
        """
        Intersect aoi for each cutoff.

        :return: A GeoDataFrame of the aoi for each cutoff.

        """

        aoi_gdf = self.read_aoi(self.h3_grid_gdf["h3_index"])

        if aoi_gdf is None:
            return None

        input_geometries_gdf_3857 = self.input_geometries.to_crs("EPSG:3857")
        aoi_gdf_3857 = aoi_gdf.to_crs("EPSG:3857")
        aoi_gdf_join = input_geometries_gdf_3857.overlay(aoi_gdf_3857, how="intersection")

        return aoi_gdf_join


class OpportunityIsochroneCount(OpportunityIntersect):
    def __init__(
        self,
        input_geometries: GeoDataFrame,
        user_id: int = 0,
        user_active_upload_ids: list = [],
        scenario_id: int = 0,
        hexagon_size: int = 6,
    ):
        """Intersect opportunity data with geometries.

        Args:
            input_geometries (GeoDataFrame): Geometries to intersect with opportunity data.
            user_id (int, optional): The user id. Defaults to 0.
            user_active_upload_ids (list, optional): The user active upload ids. Defaults to [].
            scenario_id (int, optional): The user scenario id. Defaults to 0.
            hexagon_size (int, optional): The hexagon size of parque tiles. Defaults to 6.
        """
        OpportunityIntersect.__init__(
            self, input_geometries, user_id, user_active_upload_ids, scenario_id, hexagon_size
        )

    def count_poi(self, group_by_column: str):
        """
        Count the number of poi for each cutoff.

        :param group_by: The input_geometries column to group by.

        :return: A dictionary with the cummulative number of opportunities for each cutoff .

        """
        poi_gdf = self.poi()
        poi_count = defaultdict(dict)
        # Poi with one entrance.
        poi_one_entrance_gdf = poi_gdf[poi_gdf["entrance_type"] == "one"]
        poi_one_entrance_gdf_grouped = poi_one_entrance_gdf.groupby([group_by_column, "category"])[
            "uid"
        ].count()

        for (key, category), value in poi_one_entrance_gdf_grouped.items():
            poi_count[key][category] = value

        # Poi with multiple entrances.
        poi_multiple_entrances_gdf = poi_gdf[poi_gdf["entrance_type"] == "multiple"]

        agg_func = {}
        if group_by_column == "minute" or group_by_column == "steps":
            # relevant for isochrone inputs
            agg_func_ = {"minute": "mean", "steps": "min"}
            agg_func = agg_func_[group_by_column]
        else:
            # case when a multi entrance poi is in multiple shapes
            agg_func = {group_by_column: "_".join}

        poi_multiple_entrances_gdf_grouped = (
            poi_multiple_entrances_gdf.groupby(["category", "name"]).agg(agg_func).reset_index()
        )
        if group_by_column == "minute" or group_by_column == "steps":
            poi_multiple_entrances_gdf_grouped[
                group_by_column
            ] = poi_multiple_entrances_gdf_grouped[group_by_column].astype(int)

        poi_multiple_entrances_gdf_grouped = poi_multiple_entrances_gdf_grouped.groupby(
            [group_by_column, "category"]
        )["name"].count()
        for (key, category), value in poi_multiple_entrances_gdf_grouped.items():
            poi_count[key][category] = value

        return dict(poi_count)

    def count_population(self, group_by_columns: list[str]):
        """
        Count the number of population for each cutoff.

        :param group_by: The input_geometries column to group by.

        :return: A dictionary with the cummulative number of opportunities for each cutoff.

        """
        population_count = defaultdict(dict)
        population_gdf_join = self.population()
        population_gdf_grouped = population_gdf_join.groupby(group_by_columns).agg(
            {"population": "sum"}
        )
        for key, value in population_gdf_grouped.iterrows():
            population_count[key]["population"] = value["population"]

        return dict(population_count)

    def count_aoi(self, group_by_columns: list[str]):
        """
        Count the number of aoi for each cutoff.

        :param group_by: The input_geometries column to group by.

        :return: A dictionary with the cummulative number of opportunities for each cutoff.

        """

        aoi_count = defaultdict(dict)
        aoi_gdf = self.aoi()
        if aoi_gdf is None or len(aoi_gdf) == 0:
            return dict(aoi_count)
        aoi_gdf_grouped = aoi_gdf.groupby(group_by_columns).apply(lambda x: x.area.sum())
        for (key, category), value in aoi_gdf_grouped.items():
            aoi_count[key][category] = value

        return dict(aoi_count)


opportunity = Opportunity()
