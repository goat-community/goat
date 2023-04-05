from src.core.config import settings
from src.db.migration.file_migration import FileMigration
from src.db.session import legacy_engine


def file_migration():
    """Temporary script to execute data migration from the database to parquet files."""

    input_config = {
        "mask_config": "SELECT ST_Union(geom) as geom FROM basic.study_area",
        "h3_bulk_resolution": 6,
        "h3_child_resolution": 10,
        "mask_buffer_distance": 6000,
        "layer_config": {
            "original": {
                "poi": "SELECT * FROM basic.poi",
                "population": "SELECT * FROM basic.population",
                "aoi": "SELECT * FROM basic.aoi",
            },
            "grid": {
                "population": "SELECT SUM(population) AS value FROM basic.population p",
            },
            "analysis_unit": {
                "h3": "SELECT * FROM basic.study_area"
            },
        },
        "upload_to_s3": True,
        "s3_folder": "prod",
    }

    mask_config = input_config["mask_config"]
    h3_bulk_resolution = input_config["h3_bulk_resolution"]
    h3_child_resolution = input_config["h3_child_resolution"]
    mask_buffer_distance = input_config["mask_buffer_distance"]
    layer_config = input_config["layer_config"]
    output_dir = settings.OPPORTUNITY_PATH
    boto3 = settings.S3_CLIENT

    FileMigration(
        legacy_engine,
        boto3,
        layer_config,
        mask_config,
        mask_buffer_distance,
        h3_bulk_resolution,
        h3_child_resolution,
        output_dir,
        upload_to_s3=input_config["upload_to_s3"],
        s3_folder=input_config["s3_folder"],
    ).run()


file_migration()
