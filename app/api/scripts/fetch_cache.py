import geopandas as gpd
from src.utils import create_h3_grid
from src.db.session import legacy_engine
from src.utils import print_info, print_warning
from pathlib import Path
from src.core.config import settings


config = {
    "bucket_name": "plan4better-data",
    "s3_folder": "prod",
    "study_area_ids": [91620000],
    "modes": ["walking"],
    "opportunity_data": {
        "grid": ["population"],
        "original": ["poi", "aoi", "population", "population_grouped"],
    },
}

_opportunity_matrices_relations = [
    "grid_ids",
    "weight",
    "relation_size",
    "travel_times",
    "uids",
    "names",
    "categories",
]

_opportunity_matrices_layers = ["poi", "population", "aoi"]


def download_files(s3_client, bucket_name, subfolder, local_path, file_names):

    local_path = Path(local_path)

    for file_name in file_names:
        file_path = Path.joinpath(local_path, file_name)
        s3_file_path = Path.joinpath(Path(subfolder), file_name)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            print_info(f"Downloading {file_name}...")
            s3_client.download_file(bucket_name, str(s3_file_path), str(file_path))
        except Exception as e:
            print_warning(f"Failed to download {file_name}: {e}")


def fetch_cache():

    # - Get study area geom from database
    study_area_geom = gpd.GeoDataFrame.from_postgis(
        f"SELECT geom FROM basic.study_area sa WHERE sa.id = any(array{config['study_area_ids']})",
        legacy_engine,
    )
    study_area_h3_grid_ids = create_h3_grid(
        geometry=study_area_geom.unary_union,
        h3_resolution=6,
        intersect_with_centroid=True,
    )["h3_index"].tolist()

    bulk_ids = list(set(study_area_h3_grid_ids))

    file_names = []

    # Fetch analysis unit
    for study_area_id in config["study_area_ids"]:
        for resolution in range(6, 10 + 1):
            file_names.append(f"analysis_unit/{study_area_id}/h3/{resolution}_grids.npy")
            file_names.append(f"analysis_unit/{study_area_id}/h3/{resolution}_polygons.npy")

    for bulk_id in bulk_ids:
        # Fetch travel time matrices
        for mode in config["modes"]:
            file_names.append(f"traveltime_matrices/{mode}/standard/{bulk_id}.npz")

        # Fetch opportunity data
        for layer_type in config["opportunity_data"]:
            for layer in config["opportunity_data"][layer_type]:
                if layer_type == "grid":
                    file_names.append(f"opportunity/{layer_type}/{bulk_id}/{layer}.npz")
                elif layer_type == "original":
                    file_names.append(f"opportunity/{layer_type}/{bulk_id}/{layer}.parquet")
                else:
                    raise ValueError(f"Unknown layer type: {layer_type}")

        # Fetch opportunity matrices
        for mode in config["modes"]:
            for layer in _opportunity_matrices_layers:
                for relation in _opportunity_matrices_relations:
                    file_names.append(
                        f"opportunity_matrices/{mode}/standard/{bulk_id}/{layer}/{relation}.npy"
                    )

        # Fetch connectivity matrices
        for mode in config["modes"]:
            file_names.append(f"connectivity_matrices/{mode}/standard/{bulk_id}.npz")

    # Download files
    download_files(
        settings.S3_CLIENT,
        config["bucket_name"],
        config["s3_folder"],
        settings.CACHE_DIR,
        file_names,
    )

    print_info("Done")


fetch_cache()
