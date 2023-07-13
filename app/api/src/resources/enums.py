from enum import Enum


class ReturnType(str, Enum):
    """ "Default return types"""

    geojson = "geojson"
    geobuf = "geobuf"


class IndicatorResultsReturnType(str, Enum):
    """Combination of Heatmap and Isochrone Return Types"""

    GRID = "grid"
    GEOJSON = "geojson"
    NETWORK = "network"

    CSV = "csv"
    GEOBUF = "geobuf"
    SHAPEFILE = "shapefile"
    GEOPACKAGE = "geopackage"
    KML = "kml"
    XLSX = "xlsx"


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

    max_upload_poi_file_size = 5242880  # in bytes


class IsochroneExportType(str, Enum):
    """Supported files types for export."""

    CSV = "csv"
    GEOBUF = "geobuf"
    SHAPEFILE = "shapefile"
    GEOPACKAGE = "geopackage"
    KML = "kml"
    XLSX = "xlsx"


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

    sub_study_area = "sub_study_area"
    study_area = "study_area"


class IsochroneTypes(str, Enum):
    """Isochrone Types Enums."""

    single = "single"
    multi = "multi"


class R5DecayFunctionType(str, Enum):
    logistic = "logistic"
    step = "step"
    exponential = "exponential"
    linear = "linear"


class StaticTableSQLActive(str, Enum):
    """Static Table SQL that can be requested by study_area_id."""

    study_area = """
        SELECT * FROM basic.study_area WHERE id = :study_area_id
    """
    sub_study_area = """
        SELECT * FROM basic.sub_study_area WHERE study_area_id = :study_area_id
    """


class SQLReturnTypes(str, Enum):
    """Allowed Vector Tables Enums."""

    db_geobuf = """
    WITH make_geobuf AS
    (
        %s
    )
    SELECT ST_AsGeobuf(g.*, 'geom')
    FROM make_geobuf g;
    """
    geojson = """
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
    geobuf = """WITH make_geojson AS
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

    geojson = ".geojson"
    zip = ".zip"


class SettingToModify(str, Enum):
    """Setting to reset."""

    poi = "poi"


class LanguageEnum(str, Enum):
    """Language Enum."""

    en = "en"
    de = "de"


class UpdateTableFunction(str, Enum):
    """Update Table Functions."""

    # The order of the functions is important.
    opportunity_config = "update_opportunity_config"
    layer_library = "update_layer_library"
    customization = "update_customization"

    aoi = "update_aoi"
    poi = "update_poi"
    study_area = "update_study_area"
    heatmap = "update_heatmap"
    all = "all"


class LayerGroupsEnum(str, Enum):
    buildings_landuse = "buildings_landuse"
    street_level_quality = "street_level_quality"
    environmental_quality = "environmental_quality"
    additional_data = "additional_data"
    basemap = "basemap"
    indicator = "indicator"


class GeostoreType(str, Enum):
    geoadmin = "geoadmin"
    other = "other"


class SystemStatus(str, Enum):
    maintenance = "maintenance"
    running = "running"


class OpportunityHeatmapTypes(str, Enum):
    """Opportunity type for the heatmap."""

    poi = "poi"
    poi_user = "poi_user"
    aoi = "aoi"
    population = "population"


class MigrationTables(str, Enum):
    """Migration Tables."""

    poi = "poi"
    aoi = "aoi"
    study_area = "study_area"
    sub_study_area = "sub_study_area"
    population = "population"
    building = "building"
