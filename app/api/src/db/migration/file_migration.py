from pathlib import Path
from time import strftime
from typing import Any

import geopandas as gpd
import h3
import numpy as np
import pandas as pd
from shapely.geometry import Polygon

from src.core.config import settings
from src.utils import print_info, print_warning, h3_to_int


class FileMigration:
    """
    Export data from the database to parquet files. Each layer is tiled with H3 based and stored in a separate parquet file.
    The parquet files are stored in a directory structure that is compatible with H3 grid ids which can be loaded for later use.
    Optionally the data can be filtered by a mask geometry.
    """

    def __init__(
        self,
        db,
        boto3,
        layer_config: dict,
        mask_config: str,
        mask_buffer_distance: int = 0,
        h3_bulk_resolution: int = 6,
        h3_child_resolution: int = 10,
        output_dir: str = "/app/src/cache/opportunity",
        upload_to_s3: bool = False,
        s3_folder: str = "",
    ):
        """Initialize the Export class

        Args:
            db (Database): Database Engine (local or remote)
            boto3 (Boto3): Boto3 Client for uploading data to S3
            layer_config (dict): Layer configuration for the export. The keys are the layer names and the values are the SQL queries, GeoJSON or Shapefile file path.
            h3_bulk_resolution (int, optional): H3 Grid resolution. Defaults to 6.
            mask_config (dict, optional): Mask configuration as SQL query string, GeoJSON or Shapefile file path. Defaults to None.
            mask_buffer_distance (int, optional): Mask buffer distance in meters. Defaults to None.
            output_dir (str, optional): Output directory. Defaults to "../data/output".
            upload_to_s3 (bool, optional): Upload data to S3. Defaults to False.
            s3_folder (str, optional): Upload data to S3. Default root
        """
        self.db = db
        self.boto3 = boto3
        self.layer_config = layer_config
        self.h3_bulk_resolution = h3_bulk_resolution
        self.h3_child_resolution = h3_child_resolution
        self.mask_config = mask_config
        self.mask_buffer_distance = mask_buffer_distance
        self.output_dir = output_dir
        self.upload_to_s3 = upload_to_s3
        self.s3_folder = s3_folder

    def prepare_mask(self, mask_config: str, buffer_distance: int = 0, db: Any = None):
        """Prepare mask geometries
        Args:
            mask_config (str): Path to a GeoJSON file or a PostGIS query
            buffer_distance (int, optional): Buffer distance in meters. Defaults to 0.
            db (Any, optional): Database connection. Defaults to None.
        Returns:
            [GeoDataFrame]: Returns a GeoDataFrame with the mask geometries as polygons
        """
        if Path(mask_config).is_file():
            mask_geom = gpd.read_file(mask_config)
        else:
            try:
                mask_geom = gpd.GeoDataFrame.from_postgis(mask_config, db)
            except Exception as e:
                print_warning(f"Error while reading mask geometry")
        mask_gdf = gpd.GeoDataFrame.from_features(mask_geom, crs="EPSG:4326")
        mask_gdf = mask_gdf.to_crs("EPSG:3857")
        mask_gdf.geometry = mask_gdf.geometry.buffer(buffer_distance)
        mask_gdf = mask_gdf.to_crs("EPSG:4326")
        mask_gdf = mask_gdf.explode(index_parts=True)
        return mask_gdf

    def _create_h3_indexes(self, grid_ids: list[str]) -> gpd.GeoDataFrame:
        """Create a GeoDataFrame with H3 indexes and the corresponding geometries

        Args:
            grid_ids (list[str])): List of H3 indexes

        Returns:
            [GeoDataFrame]: Returns a GeoDataFrame with the H3 indexes and the corresponding geometries
        """

        h3_indexes_gdf = gpd.GeoDataFrame(
            columns=["grid_id", "geometry"], geometry="geometry", crs="EPSG:4326"
        )
        h3_indexes_gdf["grid_id"] = grid_ids
        h3_indexes_gdf["geometry"] = h3_indexes_gdf["grid_id"].apply(
            lambda x: Polygon(h3.h3_to_geo_boundary(h=str(x), geo_json=True))
        )
        return h3_indexes_gdf

    def _create_h3_index_mask(self, mask_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Create a list of H3 indexes with geometries based on a mask geometry

        Args:
            mask_gdf ([GeoDataFrame]): Mask geometries

        Returns:
            [GeoDataFrame]: Returns a GeoDataFrame with the H3 indexes and the corresponding geometries
        """      

        h3_indexes = []
        for row in mask_gdf.__geo_interface__["features"]:
            grid_id = h3.polyfill(row["geometry"], self.h3_bulk_resolution, geo_json_conformant=True)
            h3_indexes.extend(grid_id)
        h3_indexes = list(set(h3_indexes))
        return self._create_h3_indexes(h3_indexes)

    def _read_from_postgis(self, input_sql: str, clip: str = None):
        """Read a layer from the database

        Args:
            input_sql (str): SQL query
            clip (str, optional): Clip geometry as WKT. Defaults to None.

        Returns:
            [GeoDataFrame]: Returns a GeoDataFrame with the layer data
        """
        if clip:
            query_sql = (
                input_sql
                + " WHERE ST_Intersects(ST_SETSRID(ST_GEOMFROMTEXT('"
                + clip
                + "'), 4326), geom)"
            )
        else:
            query_sql = input_sql
        h3_gdf = gpd.read_postgis(query_sql, self.db)
        return h3_gdf

    def _group_from_postgis(self, input_sql: str, clip: list[str] = None, group_by: list[str] = None):
        """Read a layer from the database

        Args:
            input_sql (str): SQL query
            clip (str, optional): Clip geometry as WKT. Defaults to None.

        Returns:
            [DataFrame]: Returns a DataFrame with the data grouped by H3 index
        """
        if clip:
            query_sql = (
                f"""
                WITH h3_grid AS (
                    SELECT ST_SETSRID(ST_GEOMFROMTEXT(geom_text), 4326) AS geom, grid_id
                    FROM (SELECT UNNEST(ARRAY[{clip}]) AS geom_text, UNNEST(ARRAY[{group_by}]) AS grid_id) x 
                )
                SELECT grid_id, g.*
                FROM h3_grid
                CROSS JOIN LATERAL (
                    {input_sql}
                    WHERE ST_Intersects(p.geom, h3_grid.geom)
                    GROUP BY grid_id
                ) AS g
                """
            )
        else:
            query_sql = input_sql
        
        df_grouped = pd.read_sql(query_sql, self.db)
        return df_grouped  


    def _export_original(self, h3_indexes_gdf: gpd.GeoDataFrame, export_metadata_gdf: gpd.GeoDataFrame, layer_input: dict) -> gpd.GeoDataFrame:
        """Export the data unchanged for the H3 indexes and saves them in parquet files 

        Args:
            h3_indexes_gdf (gpd.GeoDataFrame): GeoDataFrame with the H3 indexes and the corresponding geometries
            export_metadata_gdf (gpd.GeoDataFrame): GeoDataFrame with the export metadata
            layer_input (dict): Dictionary with the layer names and the SQL queries

        Returns:
            gpd.GeoDataFrame: Returns a GeoDataFrame with the export metadata
        """          

        for index, row in h3_indexes_gdf.iterrows():
            print_info(f"Processing original export for H3 index {row['grid_id']}")
            h3_output_file_dir = Path(self.output_dir, "original", row["grid_id"])
            h3_output_file_dir.mkdir(parents=True, exist_ok=True)
            for layer_name, layer_source in layer_input.items():
                print(f"Processing {layer_name} for H3 index {row['grid_id']}")
                filename = layer_name + ".parquet"
                try:
                    if isinstance(layer_source, str):
                        layer_source = self._read_from_postgis(
                            layer_source, row["geometry"].wkt
                        )
                  
                    if len(layer_source) != 0:
                        h3_gdf = gpd.clip(layer_source, row["geometry"])
                        # for poi layer, convert tags to str type. Parquet doesn't support dict type for some reason TODO: fix this
                        if layer_name == "poi":
                            h3_gdf["tags"] = h3_gdf["tags"].astype(str)
                        h3_gdf.to_parquet(h3_output_file_dir / filename)
                        
                        if self.upload_to_s3 == True:
                            # Save to S3
                            self.boto3.upload_file(
                                "{}/{}".format(h3_output_file_dir, filename),
                                settings.AWS_BUCKET_NAME,
                                "{}/{}/{}/{}".format(
                                    self.s3_folder, "original", row["grid_id"], filename
                                ),
                            )
                        status = "success"
                    else:
                        status = "no_data"
                except Exception as e:
                    message = f'Processing {layer_name} for H3 index {row["grid_id"]}'
                    print_warning(message)
                    status = "error"
                finally:
                    export_metadata_gdf.loc[row["grid_id"], layer_name] = status
        
        return export_metadata_gdf
       
    def _export_grid(self, h3_indexes_gdf: gpd.GeoDataFrame, export_metadata_gdf: gpd.GeoDataFrame, layer_input: dict) -> gpd.GeoDataFrame:
        """Groups data on H3 index level and saves them in npz files

        Args:
            h3_indexes_gdf (gpd.GeoDataFrame): GeoDataFrame with the H3 indexes and the corresponding geometries
            export_metadata_gdf (gpd.GeoDataFrame): GeoDataFrame with the export metadata
            layer_input (dict): Dictionary with the layer names and the SQL queries

        Returns:
            gpd.GeoDataFrame: Returns a GeoDataFrame with the export metadata
        """        

        # Get list of H3 indexes
        h3_parent_ids = h3_indexes_gdf["grid_id"].tolist()
        batch_size = 500
        
        for parent_id in h3_parent_ids:
            print_info(f"Processing grid export for H3 index {parent_id}")

            for layer_name, layer_source in layer_input.items():
                print(f"Processing {layer_name} for H3 index {parent_id}")

                # Create output directory
                h3_output_file_dir = Path(self.output_dir, "grid", parent_id)
                h3_output_file_dir.mkdir(parents=True, exist_ok=True)

                # Create output filename
                filename = layer_name
            
                # Get list of children
                h3_children = list(h3.h3_to_children(parent_id, self.h3_child_resolution))

                # Get geometries of children
                h3_children_gdf = self._create_h3_indexes(h3_children)
                
                # Get list of WKT geometries of children
                h3_children_wkt = h3_children_gdf["geometry"].apply(lambda x: x.wkt).tolist()

                # Convert children numpy array of object 
                h3_children = np.array(h3_children, dtype=object)
                h3_children = h3_to_int(h3_children)
                # Create empty arrays
                arr_grid_id = []
                arr_value = []

                try:
                    if isinstance(layer_source, str):
                        # Read from PostGIS in bulks 
                        for i in range(0, len(h3_children_wkt), batch_size):
                            h3_children_wkt_bulk = h3_children_wkt[i:i+batch_size]
                            h3_children_bulk = list(h3_children[i:i+batch_size])
                            grouped_df = self._group_from_postgis(layer_input[layer_name], h3_children_wkt_bulk, h3_children_bulk)
                            # Check value is not empty
                            grouped_df = grouped_df[grouped_df["value"].notna()]
                            arr_grid_id.extend(grouped_df["grid_id"].tolist())
                            arr_value.extend(grouped_df["value"].tolist())
                        
                        # Convert to numpy array
                        arr_grid_id = np.array(arr_grid_id)
                        arr_value = np.array(arr_value)

                    if arr_grid_id.size != 0:
                        # Save numpy to files 
                        np.savez(h3_output_file_dir / filename, **{"grid_id": arr_grid_id, "value": arr_value})

                        if self.upload_to_s3 == True:
                            # Save to S3
                            self.boto3.upload_file(
                                "{}/{}".format(h3_output_file_dir, filename + ".npz"),
                                settings.AWS_BUCKET_NAME,
                                "{}/{}/{}/{}".format(
                                    self.s3_folder, "grid", parent_id, filename + ".npz"
                                ),
                            )
                        status = "success"
                    else:
                        status = "no_data"
                except Exception as e:
                    message = f'Processing {layer_name} for H3 index {parent_id}'
                    print_warning(message)
                    status = "error"
                finally:
                    export_metadata_gdf.loc[parent_id, layer_name] = status
    
        return export_metadata_gdf


    def _export(self, h3_indexes_gdf: gpd.GeoDataFrame):
        """Export the layers to parquet files

        Args:
            h3_indexes_gdf ([GeoDataFrame]): H3 indexes
        """
        # Build layer input
        layer_input = {"original": {}, "grid": {}}
        for export_type in layer_input.keys():
            for layer_name, layer_source in self.layer_config[export_type].items():
                if Path(layer_source).is_file():
                    layer_input[export_type][layer_name] = gpd.read_file(layer_source)
                else:
                    layer_input[export_type][layer_name] = layer_source
                
        #TODO: Fix metadata creation
        # Create metadata dataframe
        export_metadata_gdf = h3_indexes_gdf.assign(
            **{k: "" for k in self.layer_config["original"].keys()}
        )
        export_metadata_gdf.set_index("grid_id", inplace=True)
       
        # Export data
        #export_metadata_gdf = self._export_original(h3_indexes_gdf, export_metadata_gdf, layer_input["original"])
        export_metadata_gdf = self._export_grid(h3_indexes_gdf, export_metadata_gdf, layer_input["grid"])      

        #TODO: Fix export metadata
        # Save metadata
        export_metadata_gdf.to_file(
            Path(self.output_dir, f"metadata_{strftime('%d-%b-%Y_%Hh%Mm%Ss')}.geojson"),
            driver="GeoJSON",
        )
        export_metadata_gdf.to_csv(
            Path(self.output_dir, f"metadata_{strftime('%d-%b-%Y-%H-%M-%S')}.csv"),
            columns=list(set(export_metadata_gdf.columns) - set(["geometry"])),
            index=True,
        )

    def run(self):
        """Run the export"""
        print_info("PREPARING MASK")
        mask_gdf = self.prepare_mask(self.mask_config, self.mask_buffer_distance, self.db)
        print_info("CREATING H3 INDEXES")
        h3_indexes_gdf = self._create_h3_index_mask(mask_gdf)
        print_info("EXPORTING LAYERS")
        self._export(h3_indexes_gdf)
        print_info("DONE")
