from enum import Enum

from src.db.models import scenario


class ReturnType(str, Enum):
    """"Default return types"""
    geojson = "geojson"
    geobuf = "geobuf"
    db_geobuf = "db_geobuf"

class ReturnWithoutDbGeobufEnum(str, Enum):
    """Enumeration for return types without db geobuf."""
    geojson = "geojson"
    geobuf = "geobuf"

class VectorType(str, Enum):
    """Vector Type Enums."""

    pbf = "pbf"
    mvt = "mvt"

class AccessibilityHeatmapTypes(str, Enum):
    """Heatmap Type Enums."""

    local_accessibility = "heatmap_local_accessibility"
    local_accessibility_population = "heatmap_accessibility_population"

class MaxUploadFileSize(int, Enum):
    """Maximum upload file size."""

    max_upload_poi_file_size = 5242880 # in bytes

class IsochroneExportType(str, Enum):
    """Supported files types for export."""

    geojson = "GeoJSON"
    shp = "ESRI Shapefile"
    xlsx = "XLSX"

class CalculationTypes(str, Enum):
    """Calculation types for indicators."""

    default = "default"
    scenario = "scenario"
    comparison = "comparison"

class RoutingTypes(str, Enum):
    """Calculation types for indicators."""

    walking_standard = "walking_standard"
    walking_wheelchair = "walking_wheelchair"
    cycling_standard = "cycling_standard"
    cycling_pedelec = "cycling_pedelec"


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

class SettingToModify(str, Enum):
    """Setting to reset."""
    poi = "poi_groups"