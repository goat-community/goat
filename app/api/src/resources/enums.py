from enum import Enum


class VectorType(str, Enum):
    """Vector Type Enums."""

    pbf = "pbf"
    mvt = "mvt"

class AllowedVectorTables(str, Enum):
    """Allowed Vector Tables Enums."""
    sub_study_area = "basic.sub_study_area"

class SQLReturnTypes(str, Enum):
    """Allowed Vector Tables Enums."""
    db_geobuf = f"""
    WITH make_geobuf AS
    (
        %s
    )
    SELECT ST_AsGeobuf(g.*, 'geom')
    FROM make_geobuf g;
    """
    geojson = f"""
    WITH make_geojson AS 
    (
        %s
    )
    SELECT json_build_object
    (
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(g.*)::json)
    ) 
    FROM make_geojson g; 
    """
    geobuf = f"""WITH make_geojson AS 
    (
        %s
    )
    SELECT json_build_object
    (
        'type', 'FeatureCollection',
        'features', json_agg(ST_AsGeoJSON(g.*)::json)
    ) 
    FROM make_geojson g; 
    """

class MimeTypes(str, Enum):
    """Responses MineTypes."""

    xml = "application/xml"
    json = "application/json"
    geojson = "application/geo+json"
    html = "text/html"
    text = "text/plain"
    pbf = "application/x-protobuf"
    mvt = "application/x-protobuf"
    geobuf = "application/geobuf.pbf"

class UploadFileTypes(str, Enum):
    """Upload File Types."""

    geojson = "application/geo+json"
    zip = "application/zip" 