# Standard library imports
from enum import Enum
from typing import Annotated, List, Literal, Optional, Union
from uuid import UUID, uuid4

# Third party imports
from pydantic import (
    BaseModel,
    Field,
    HttpUrl,
    ValidationError,
    ValidationInfo,
    field_validator,
)
from pyproj import CRS
from pyproj.exceptions import CRSError
from shapely import wkt

# Local application imports
from core.db.models._base_class import DateTimeBase, content_base_example
from core.db.models.layer import (
    DataCategory,
    DataLicense,
    FeatureDataType,
    FeatureGeometryType,
    FeatureLayerExportType,
    FeatureType,
    GeospatialAttributes,
    LayerBase,
    LayerType,
    RasterDataType,
    TableLayerExportType,
    ToolType,
    layer_base_example,
    validate_geographical_code,
    validate_language_code,
)
from core.schemas.common import CQLQuery
from core.schemas.job import Msg
from core.utils import optional


class MaxFileSizeType(int, Enum):
    """Max file size types in bytes."""

    geojson = 300000000
    csv = 100000000
    xlsx = 100000000
    gpkg = 300000000
    kml = 300000000
    zip = 300000000


class SupportedOgrGeomType(Enum):
    Point = "point"
    Multi_Point = "point"
    Line_String = "line"
    Multi_Line_String = "line"
    Polygon = "polygon"
    Multi_Polygon = "polygon"


class UserDataGeomType(Enum):
    point = "point"
    line = "line"
    polygon = "polygon"
    no_geometry = "no_geometry"


class OgrPostgresType(str, Enum):
    Integer = "integer"
    Integer64 = "bigint"
    Real = "float"
    String = "text"
    Date = "text"
    Time = "text"
    DateTime = "timestamp"


class OgrDriverType(str, Enum):
    """OGR driver types."""

    geojson = "GeoJSON"
    csv = "CSV"  # Using XLSX driver for CSV files as the file is converted to XLSX to keep data types
    xlsx = "XLSX"
    gpkg = "GPKG"
    kml = "KML"
    shp = "ESRI Shapefile"  # Using SHP driver for ZIP files as the file is converted to SHP to keep data types
    zip = "ESRI Shapefile"  # Using SHP driver for ZIP files as the file is converted to SHP to keep data types


class NumberColumnsPerType(int, Enum):
    """Number of columns per type."""

    integer = 25
    bigint = 5
    float = 25
    text = 25
    timestamp = 3
    arrfloat = 3
    arrint = 3
    arrtext = 3
    jsonb = 10
    boolean = 10


class ComputeBreakOperation(Enum):
    """Allowed operations on numeric columns."""

    quantile = "quantile"
    standard_deviation = "standard_deviation"
    equal_interval = "equal_interval"
    heads_and_tails = "heads_and_tails"


class AreaStatisticsOperation(Enum):
    """Allowed operations on polygon geometries."""

    sum = "sum"
    min = "min"
    max = "max"


class UserDataTable(str, Enum):
    """Created user tables"""

    point = "point"
    line = "line"
    polygon = "polygon"
    no_geometry = "no_geometry"
    street_network_line = "street_network_line"
    street_network_point = "street_network_point"


class LayerReadBaseAttributes(BaseModel):
    id: UUID = Field(..., description="Content ID of the layer")
    user_id: UUID = Field(..., description="User ID of the owner")
    shared_with: dict | None = Field(
        None, description="List of user IDs the layer is shared with"
    )
    owned_by: dict | None = Field(None, description="User ID of the owner")


class LayerProperties(BaseModel):
    """Base model for layer properties."""

    type: str = Field(..., description="Mapbox style type", max_length=500)
    paint: dict = Field(..., description="Paint of the mapbox style of the layer")


################################################################################
# External service DTOs
################################################################################


class ExternalServiceOtherProperties(BaseModel):
    """Model for external service properties."""

    url: str | None = Field(
        default=None,
        description="Layer URL",
    )
    layers: List[str] | None = Field(
        default=None,
        description="List of layers to be displayed",
    )
    width: int | None = Field(
        default=None,
        description="Width of the WMS image",
    )
    height: int | None = Field(
        default=None,
        description="Height of the WMS image",
    )
    srs: str | None = Field(
        default=None,
        description="SRS of the WMS image",
        max_length=50,
    )
    legend_urls: List[str] | None = Field(
        default=None,
        description="Layer legend URLs",
    )

    @field_validator("url", mode="before")
    def convert_url_httpurl_to_str(cls, value: str | HttpUrl | None) -> str | None:
        if value is None:
            return value
        elif isinstance(value, HttpUrl):
            return str(value)
        assert HttpUrl(value)
        return value

    @field_validator("legend_urls", mode="before")
    def convert_legend_urls_httpurl_to_str(cls, value: list[str] | list[HttpUrl] | None) -> list[str] | None:
        if value is None:
            return value

        result = []
        for v in value:
            if isinstance(v, HttpUrl):
                result.append(str(v))
            else:
                assert HttpUrl(v)
                result.append(v)
        return result


class ExternalServiceAttributesBase(BaseModel):
    """Base model for attributes pertaining to an external service."""

    url: str | None = Field(
        default=None,
        description="Layer URL",
    )
    data_type: FeatureDataType | RasterDataType | None = Field(
        default=None,
        description="Content data type",
    )
    other_properties: ExternalServiceOtherProperties | None = Field(
        default=None,
        description="Additional layer properties.",
    )

    @field_validator("url", mode="before")
    def convert_httpurl_to_str(cls, value: str | HttpUrl | None) -> str | None:
        if value is None:
            return value
        elif isinstance(value, HttpUrl):
            return str(value)
        assert HttpUrl(value)
        return value


################################################################################
# File Upload DTOs
################################################################################


class IFileUploadExternalService(ExternalServiceAttributesBase):
    """Model for external service attributes used to fetch feature data and save it as a file."""

    pass


class IFileUploadMetadata(BaseModel):
    """Response model returned by file upload endpoints containing dataset metadata."""

    data_types: dict = Field(..., description="Data types of the columns")
    layer_type: LayerType = Field(..., description="Layer type")
    file_ending: str = Field(..., description="File ending", max_length=500)
    file_size: int = Field(..., description="File size")
    file_path: str = Field(..., description="File path", max_length=500)
    dataset_id: UUID = Field(..., description="Dataset ID")
    msg: Msg = Field(..., description="Response Message")


################################################################################
# Feature Layer DTOs
################################################################################


class FeatureReadBaseAttributes(
    LayerReadBaseAttributes, LayerBase, GeospatialAttributes
):
    """Base model for feature layer reads."""

    feature_layer_geometry_type: "FeatureGeometryType" = Field(
        ..., description="Feature layer geometry type"
    )
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")
    size: int = Field(..., description="Size of the layer in bytes")
    properties: dict = Field(..., description="Layer properties.")


class FeatureUpdateBase(LayerBase, GeospatialAttributes):
    """Base model for feature layer updates."""

    properties: dict | None = Field(None, description="Layer properties.")


feature_layer_update_base_example = {
    "properties": [
        "match",
        ["get", "category"],
        ["forest"],
        "hsl(137, 37%, 30%)",
        ["park"],
        "hsl(135, 100%, 100%)",
        "#000000",
    ],
    "size": 1000,
}


# Feature Layer Standard
class ILayerFromDatasetCreate(LayerBase, ExternalServiceAttributesBase):
    id: UUID = Field(
        default_factory=uuid4,
        description="Content ID of the layer",
        alias="id",
    )
    dataset_id: UUID = Field(
        ...,
        description="Dataset ID",
    )
    properties: Optional[dict] = Field(
        default=None,
        description="Layer properties.",
    )


class IFeatureLayerToolCreate(BaseModel):
    id: UUID = Field(
        default_factory=uuid4, description="Content ID of the layer", alias="id"
    )
    name: str = Field(..., description="Layer name", max_length=500)
    feature_layer_geometry_type: FeatureGeometryType = Field(
        ..., description="Feature layer geometry type"
    )
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")
    tool_type: ToolType = Field(..., description="Tool type")
    job_id: UUID = Field(..., description="Job ID")


class IFeatureStandardCreateAdditionalAttributes(BaseModel):
    """Model for second internal validation with extended attributes."""

    user_id: UUID = Field(..., description="User ID of the owner")
    type: LayerType = Field(..., description="Layer type")
    feature_layer_type: FeatureType = Field(..., description="Feature layer type")
    feature_layer_geometry_type: FeatureGeometryType = Field(
        ..., description="Feature layer geometry type"
    )
    extent: str = Field(
        ..., description="Geographical Extent of the layer", max_length=500
    )
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")


class IFeatureStandardRead(
    FeatureReadBaseAttributes, DateTimeBase, ExternalServiceAttributesBase
):

    type: Literal["feature"]
    feature_layer_type: Literal["standard"]


@optional
class IFeatureStandardUpdate(FeatureUpdateBase):
    pass


# Feature Layer Tool
class FeatureToolAttributesBase(BaseModel):
    """Base model for additional attributes feature layer tool."""

    tool_type: ToolType = Field(..., description="Tool type")


feature_layer_tool_attributes_example = {
    "tool_type": "catchment_area",
}


class IFeatureToolCreate(LayerBase, FeatureToolAttributesBase):
    """Model to create feature layer tool."""

    pass


class IFeatureToolRead(
    FeatureReadBaseAttributes, FeatureToolAttributesBase, DateTimeBase
):
    """Model to read a feature layer tool."""

    type: Literal["feature"]
    feature_layer_type: Literal["tool"]
    charts: dict | None = Field(None, description="Chart configuration")


@optional
class IFeatureToolUpdate(FeatureUpdateBase):
    """Model to update a feature layer tool."""

    pass


class IFeatureStreetNetworkRead(FeatureReadBaseAttributes, DateTimeBase):
    """Model to read a street network feature layer."""

    type: Literal["feature"]
    feature_layer_type: Literal["street_network"]


class IFeatureStreetNetworkUpdate(IFeatureStandardUpdate):
    """Model to update a street network feature layer."""

    pass


################################################################################
# Raster DTOs
################################################################################


class RasterAttributesBase(ExternalServiceAttributesBase):
    """Base model for attributes pertaining to an external service providing a raster."""

    type: LayerType = Field(..., description="Layer type")
    properties: dict | None = Field(
        {"visibility": True}, description="Layer properties."
    )

    pass


imagery_layer_attributes_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetCapabilities&service=WMS",
    "data_type": "wms",
    "properties": {
        "type": "raster",
        "paint": {"raster-opacity": 1},
    },
    "other_properties": {
        "layers": ["Actueel_ortho25"],
        "width": 256,
        "height": 256,
        "srs": "EPSG:3857",
        "legend_urls": [
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
        ],
    },
}


class IRasterCreate(LayerBase, GeospatialAttributes, RasterAttributesBase):
    """Model to create a raster layer."""

    pass


class IRasterRead(
    LayerReadBaseAttributes,
    LayerBase,
    GeospatialAttributes,
    RasterAttributesBase,
    DateTimeBase,
    ExternalServiceAttributesBase,
):
    """Model to read a raster layer."""

    type: Literal["raster"]


@optional
class IRasterUpdate(LayerBase, GeospatialAttributes):
    """Model to update a raster layer."""

    url: str | None = Field(None, description="Layer URL")
    properties: dict | None = Field(None, description="Layer properties.")
    other_properties: ExternalServiceOtherProperties | None = Field(
        None, description="Additional layer properties."
    )

    @field_validator("url", mode="before")
    def convert_httpurl_to_str(cls, value: str | HttpUrl | None) -> str | None:
        if value is None:
            return value
        elif isinstance(value, HttpUrl):
            return str(value)
        assert HttpUrl(value)
        return value


imagery_layer_update_base_example = {
    "url": "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetCapabilities&service=WMS",
    "properties": {
        "type": "raster",
        "paint": {"raster-opacity": 0.5},
        "layers": ["Actueel_ortho25"],
        "width": 256,
        "height": 256,
        "srs": "EPSG:3857",
        "legend_urls": [
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
            "https://geodata.nationaalgeoregister.nl/luchtfoto/rgb/wms?request=GetLegendGraphic&service=WMS&layer=Actueel_ortho25&format=image/png&width=20&height=20",
        ],
    },
}

################################################################################
# Table Layer DTOs
################################################################################


class ITableCreateAdditionalAttributes(BaseModel):
    """Model for second internal validation with extended attributes."""

    user_id: UUID = Field(..., description="User ID of the owner")
    type: LayerType = Field(..., description="Layer type")
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")


class ITableRead(
    LayerBase, LayerReadBaseAttributes, DateTimeBase, ExternalServiceAttributesBase
):
    """Model to read a table layer."""

    type: Literal["table"]
    attribute_mapping: dict = Field(..., description="Attribute mapping of the layer")


@optional
class ITableUpdate(LayerBase):
    """Model to update a table layer."""

    pass


def get_layer_class(class_type: str, layer_creator_class: dict, **kwargs):
    try:
        layer_type = kwargs["type"]
    except KeyError:
        raise ValidationError("Layer type is required")

    layer_class = layer_creator_class[layer_type]
    if layer_type == "feature":
        try:
            feature_layer_type = kwargs["feature_layer_type"]
        except KeyError:
            raise ValidationError("Feature layer type is required")

        layer_class = layer_class[feature_layer_type]

    layer_class_name = layer_class.__name__
    if class_type == "create":
        layer_class_name = layer_class_name.replace("Read", "Create")
    elif class_type == "update":
        layer_class_name = layer_class_name.replace("Read", "Update")
    elif class_type == "read":
        pass
    else:
        raise ValueError(f"Layer class type ({class_type}) is invalid")

    return globals()[layer_class_name]


layer_creator_class = {
    "feature": {
        "standard": IFeatureStandardRead,
        "tool": IFeatureToolRead,
        "street_network": IFeatureStreetNetworkRead,
    },
    "table": ITableRead,
    "raster": IRasterRead,
}


layer_update_class = {
    "feature": {
        "standard": IFeatureStandardUpdate,
        "tool": IFeatureToolUpdate,
        "street_network": IFeatureStreetNetworkUpdate,
    },
    "raster": IRasterUpdate,
    "table": ITableUpdate,
}


# Write function to get the correct class
def get_layer_schema(
    class_mapping: dict, layer_type: LayerType, feature_layer_type: FeatureType | None = None
):
    # Check if layer type is valid
    if layer_type in class_mapping:
        # Check if layer is feature
        if feature_layer_type:
            return class_mapping[layer_type][feature_layer_type]
        else:
            return class_mapping[layer_type]
    else:
        raise ValueError(f"Layer type ({layer_type}) is invalid")


FeatureLayer = Annotated[
    Union[
        IFeatureStandardRead,
        IFeatureToolRead,
        IFeatureStreetNetworkRead,
    ],
    Field(discriminator="feature_layer_type"),
]


ILayerRead = Annotated[
    Union[FeatureLayer, ITableRead, IRasterRead],
    Field(discriminator="type"),
]


class IUniqueValue(BaseModel):
    """Model for unique values."""

    value: str = Field(..., description="Unique value")
    count: int = Field(..., description="Number of occurrences")

    @field_validator("value", mode="before")
    def convert_value_to_str(cls, value: str | int) -> str:
        if isinstance(value, str):
            return value
        return str(value)


class IValidateJobId(BaseModel):
    """Model to import a file object."""

    validate_job_id: UUID = Field(..., description="Upload job ID")


class ILayerExport(CQLQuery):
    """Layer export input schema."""

    id: UUID = Field(..., description="Layer ID")
    file_type: FeatureLayerExportType | TableLayerExportType = Field(
        ..., description="File type"
    )
    file_name: str = Field(
        ..., description="File name of the exported file.", max_length=500
    )
    crs: str | None = Field(
        None, description="CRS of the exported file.", max_length=20
    )

    # Check if crs is valid
    @field_validator("crs")
    def validate_crs(cls, value: str | None):
        # Validate the provided CRS
        try:
            CRS(value)
        except CRSError as e:
            raise ValidationError(f"Invalid CRS: {e}")
        return value

    # Check that projection is EPSG:4326 for KML
    @field_validator("crs")
    def validate_crs_kml(cls, value: str | None, info: ValidationInfo):
        if info.data["file_type"] == FeatureLayerExportType.kml:
            if value != "EPSG:4326":
                raise ValidationError("KML export only supports EPSG:4326 projection.")
        return value


class LayerGetBase(BaseModel):
    folder_id: UUID | None = Field(
        None,
        description="Folder ID to filter by. If not specified, all layers will be returned.",
    )
    type: List[LayerType] | None = Field(
        None,
        description="Layer type to filter by. Can be multiple. If not specified, all layer types will be returned.",
    )
    feature_layer_type: List[FeatureType] | None = Field(
        None,
        description="Feature layer type to filter by. Can be multiple. If not specified, all feature layer types will be returned.",
    )
    search: str | None = Field(
        None,
        description="Searches the 'name' and 'description' column of the layer. It will convert the text into lower case and see if the passed text is part of the name.",
    )
    license: List[DataLicense] | None = Field(
        None,
        description="List of data licenses",
    )
    data_category: List[DataCategory] | None = Field(
        None,
        description="List of data categories",
    )
    geographical_code: List[str] | None = Field(
        None,
        description="List of geographical codes",
    )
    language_code: List[str] | None = Field(None, description="List of language codes")
    distributor_name: List[str] | None = Field(
        None, description="List of distributor names"
    )
    spatial_search: str | None = Field(None, description="Spatial search for the layer")
    in_catalog: Literal[True] = Field(
        True,
        description="This field is always true. Only layers that are in the catalog will be returned.",
    )

    @field_validator("language_code", mode="after", check_fields=False)
    def language_code_valid(cls, value: list[str]) -> list[str]:
        if value:
            for code in value:
                validate_language_code(code)
        return value

    @field_validator("geographical_code", mode="after", check_fields=False)
    def geographical_code_valid(cls, value: list[str]) -> list[str]:
        if value:
            for code in value:
                validate_geographical_code(code)
        return value

    # Validate the spatial search
    @field_validator("spatial_search")
    def validate_spatial_search(cls, value):
        if value:
            try:
                wkt.loads(value)
            except Exception as e:
                raise ValidationError(f"Invalid Geometry: {e}")
        return value


class ILayerGet(LayerGetBase):
    in_catalog: bool | None = Field(
        None,
        description="This field is always true. Only layers that are in the catalog will be returned.",
    )


class ICatalogLayerGet(LayerGetBase):
    in_catalog: Literal[True] = Field(
        True,
        description="This field is always true. Only layers that are in the catalog will be returned.",
    )


class IMetadataAggregate(LayerGetBase):
    pass


class MetadataGroupAttributes(BaseModel):
    value: str = Field(..., description="Name of the metadata group")
    count: int = Field(..., description="Count of the metadata group")


class IMetadataAggregateRead(BaseModel):
    license: List[MetadataGroupAttributes] = Field(..., description="List of licenses")
    data_category: List[MetadataGroupAttributes] = Field(
        ..., description="List of data categories"
    )
    geographical_code: List[MetadataGroupAttributes] = Field(
        ..., description="List of geographical codes"
    )
    language_code: List[MetadataGroupAttributes] = Field(
        ..., description="List of language codes"
    )
    type: List[MetadataGroupAttributes] = Field(..., description="List of layer types")
    distributor_name: List[MetadataGroupAttributes] = Field(
        ..., description="List of distributor names"
    )


request_examples = {
    "get": {
        "ids": [
            "e7dcaae4-1750-49b7-89a5-9510bf2761ad",
            "e7dcaae4-1750-49b7-89a5-9510bf2761ad",
        ],
    },
    "create": {
        "feature": {
            "summary": "Layer Standard",
            "value": {
                "dataset_id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                **content_base_example,
                **layer_base_example,
            },
        },
        "raster": {
            "summary": "Raster Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
                **imagery_layer_attributes_example,
                "type": "raster",
                "extent": "MULTIPOLYGON(((0 0, 0 1, 1 1, 1 0, 0 0)), ((2 2, 2 3, 3 3, 3 2, 2 2)))",
            },
        },
        "table": {
            "summary": "Table Layer",
            "value": {
                "dataset_id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                **content_base_example,
                **layer_base_example,
            },
        },
    },
    "export": {
        "feature": {
            "summary": "Layer Standard",
            "value": {
                "id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                "file_type": "csv",
                "file_name": "test",
            },
        },
        "table": {
            "summary": "Table Layer",
            "value": {
                "id": "699b6116-a8fb-457c-9954-7c9efc9f83ee",
                "file_type": "csv",
                "file_name": "test",
                "crs": "EPSG:3857",
                "query": {"op": "=", "args": [{"property": "category"}, "bus_stop"]},
            },
        },
    },
    "update": {
        "table": {
            "summary": "Table Layer",
            "value": {
                **content_base_example,
                **layer_base_example,
            },
        },
    },
}
