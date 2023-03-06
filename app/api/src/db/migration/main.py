from src.core.config import settings
from src.db.migration.file_migration import FileMigration
from src.db.session import legacy_engine


def file_migration():
    """Temporary script to execute data migration from the database to parquet files."""

    input_config = {
        "mask_config": "SELECT ST_Union(buffer_geom_heatmap) as geom FROM basic.study_area",
        "h3_bulk_resolution": 6,
        "h3_child_resolution": 10,
        "mask_buffer_distance": 0,
        "layer_config": {
            "original": {
                "poi": "SELECT * FROM basic.poi",
                "population": "SELECT * FROM basic.population",
                "aoi": "SELECT * FROM basic.aoi",
            },
            "grid": {
                "population": "SELECT SUM(population) AS value FROM basic.population",
            },
            "analysis_unit": {
                "h3": "SELECT * FROM basic.study_area"
            },
        },
        "upload_to_s3": True,
        "s3_folder": "opportunity",
    }

    mask_config = input_config["mask_config"]
    h3_bulk_resolution = input_config["h3_bulk_resolution"]
    h3_child_resolution = input_config["h3_child_resolution"]
    mask_buffer_distance = input_config["mask_buffer_distance"]
    layer_config = input_config["layer_config"]
    output_dir = "/app/src/cache/opportunity"
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

# def main():


# if __name__ == "__main__":
#     main()


# Example input_config.json


# parser = argparse.ArgumentParser(
#     description="Export data from the database to parquet files."
# )
# parser.add_argument(
#     "--input_config",
#     type=str,
#     required=True,
#     help="Json file containing input configuration",
# )
# parser.add_argument(
#     "--output_dir", type=str, default="../data/output", help="Output directory"
# )
# parser.add_argument(
#     "-u",
#     "--upload_to_s3",
#     action="store_false",
#     help="If set, the output directory will be uploaded to s3 bucket",
# )

# parser.add_argument(
#     "--s3_folder",
#     type=str,
#     default="",
#     help="If upload_to_s3 is set, the output directory will be uploaded to s3 bucket under this folder",
# )

# args = parser.parse_args()
# with open(args.input_config, "r") as f:
#     input_config = json.load(f)


# Example Run the script
# python export.py --input_config /app/src/data/input/input_config.json --output_dir /app/src/data/output --upload_to_s3 True --s3_folder parquet-tiles
