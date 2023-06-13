# MIT License

# Copyright (c) 2020 Development Seed
# Copyright (c) 2021 Plan4Better
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import abc
from dataclasses import dataclass
from typing import Any, ClassVar, Dict, List, Optional

from pydantic import BaseModel, Field
from pydantic.class_validators import root_validator
from pydantic.networks import AnyHttpUrl

from src.core.config import settings
from src.resources.enums import MimeTypes



# TODO: Refactor this part to use with the new schemas further down
# =========================VECTOR TILE SCHEMAS=========================
class VectorTileLayer(BaseModel, metaclass=abc.ABCMeta):
    """Layer's Abstract BaseClass.
    Attributes:
        id (str): Layer's name.
        bounds (list): Layer's bounds (left, bottom, right, top).
        minzoom (int): Layer's min zoom level.
        maxzoom (int): Layer's max zoom level.
        tileurl (str, optional): Layer's tiles url.

    """

    id: str
    bounds: List[float] = [-180, -90, 180, 90]
    minzoom: int = settings.DEFAULT_MINZOOM
    maxzoom: int = settings.DEFAULT_MAXZOOM
    tileurl: Optional[str]


class VectorTileTable(VectorTileLayer):
    """Table Reader.
    Attributes:
        id (str): Layer's name.
        bounds (list): Layer's bounds (left, bottom, right, top).
        minzoom (int): Layer's min zoom level.
        maxzoom (int): Layer's max zoom level.
        tileurl (str, optional): Layer's tiles url.
        type (str): Layer's type.
        schema (str): Table's database schema (e.g public).
        geometry_type (str): Table's geometry type (e.g polygon).
        geometry_column (str): Name of the geomtry column in the table.
        properties (Dict): Properties available in the table.
    """

    type: str = "Table"
    dbschema: str = Field(..., alias="schema")
    table: str
    geometry_type: str
    geometry_column: str
    properties: Dict[str, str]


class VectorTileFunction(VectorTileTable):
    """Function Reader.
    Attributes:
        id (str): Layer's name.
        bounds (list): Layer's bounds (left, bottom, right, top).
        minzoom (int): Layer's min zoom level.
        maxzoom (int): Layer's max zoom level.
        tileurl (str, optional): Layer's tiles url.
        type (str): Layer's type.
        function_name (str): Nane of the SQL function to call. Defaults to `id`.
        sql (str): Valid SQL function which returns Tile data.
        options (list, optional): options available for the SQL function.
    """

    type: str = "Function"
    sql: str
    function_name: Optional[str]
    options: Optional[List[Dict[str, Any]]]

    @root_validator
    def function_name_default(cls, values):
        """Define default function's name to be same as id."""
        function_name = values.get("function_name")
        if function_name is None:
            values["function_name"] = values.get("id")
        return values

    @classmethod
    def from_file(cls, id: str, infile: str, **kwargs: Any):
        """load sql from file"""
        with open(infile) as f:
            sql = f.read()

        return cls(id=id, sql=sql, **kwargs)


class TileMatrixSetLink(BaseModel):
    """
    TileMatrixSetLink model.

    Based on http://docs.opengeospatial.org/per/19-069.html#_tilematrixsets

    """

    href: AnyHttpUrl
    rel: str = "item"
    type: MimeTypes = MimeTypes.json

    class Config:
        """Config for model."""

        use_enum_values = True


class TileMatrixSetRef(BaseModel):
    """
    TileMatrixSetRef model.

    Based on http://docs.opengeospatial.org/per/19-069.html#_tilematrixsets

    """

    id: str
    title: str
    links: List[TileMatrixSetLink]


class TileMatrixSetList(BaseModel):
    """
    TileMatrixSetList model.

    Based on http://docs.opengeospatial.org/per/19-069.html#_tilematrixsets

    """

    tileMatrixSets: List[TileMatrixSetRef]


@dataclass
class Registry:
    """function registry"""

    funcs: ClassVar[Dict[str, VectorTileFunction]] = {}

    @classmethod
    def get(cls, key: str):
        """lookup function by name"""
        return cls.funcs.get(key)

    @classmethod
    def register(cls, *args: VectorTileFunction):
        """register function(s)"""
        for func in args:
            cls.funcs[func.id] = func


registry = Registry()


#########################################################
# =========================NEW SCHEMAS=========================
#########################################################
from typing import List, Optional
from sqlmodel import (
    ForeignKey,
    Column,
    Field,
    SQLModel,
    Text,
    Integer,
)
from uuid import UUID
from enum import Enum
from pydantic import BaseModel
from src.schemas.content import ContentUpdateBase
from src.db.models.layer import FeatureLayerBase, LayerBase, GeospatialAttributes

class OpportunityType(str, Enum):
    """Opportunity types."""

    aoi = "aoi"
    poi = "poi"
    population = "population"

class LayerType(str, Enum):
    """Layer types that are supported."""

    feature_layer = "feature_layer"
    imagery_layer = "imagery_layer"
    tile_layer = "tile_layer"
    table = "table"


class FeatureLayerType(str, Enum):
    """Feature layer types."""

    standard = "standard"
    indicator = "indicator"
    opportunity = "opportunity"
    scenario = "scenario"
    analysis_unit = "analysis_unit"


class IndicatorType(str, Enum):
    """Indicator types."""

    single_isochrone = "isochrone"
    multi_isochrone = "multi_isochrone"
    heatmap = "heatmap"
    oev_gueteklasse = "oev_gueteklasse"
    public_transport_frequency = "public_transport_frequency"


class ScenarioType(str, Enum):
    """Scenario types."""

    building = "building"
    poi = "poi"
    aoi = "aoi"
    way = "way"


class FeatureLayerDataType(str, Enum):
    """Feature layer data types."""

    geojson = "geojson"
    shapefile = "shapefile"
    geopackage = "geopackage"
    geobuf = "geobuf"
    csv = "csv"
    xlsx = "xlsx"
    kml = "kml"
    mvt = "mvt"
    wfs = "wfs"
    binary = "binary"


class ImageryLayerDataType(str, Enum):
    """Imagery layer data types."""

    wms = "wms"


class TileLayerDataType(str, Enum):
    """Tile layer data types."""

    xyz = "xyz"
    wmts = "wmts"
    mvt = "mvt"


class TableDataType(str, Enum):
    """Table data types."""

    csv = "csv"
    xlsx = "xlsx"
    json = "json"

class Opportunity(BaseModel):
    """Model to show the opportunity data sets."""

    id: UUID = Field(..., description="Layer ID of the opportunity data sets")
    name: str = Field(..., description="Opportunity name")
    opportunity_type: OpportunityType = Field(..., description="Opportunity type")
    query: Optional[str] = Field(None, description="Opportunity query to filter the data")


################################################################################
# Layer Base DTOs
################################################################################


class LayerUpdateBase(ContentUpdateBase):
    """Base model for layer updates."""

    group: Optional[str] = Field(None, description="Layer group name")
    data_source_id: Optional[int] = Field(None, description="Data source")
    data_reference_year: Optional[int] = Field(None, description="Data reference year")


################################################################################
# Feature Layer DTOs
################################################################################

class FeatureLayerReadBase(FeatureLayerBase):
    id: UUID = Field(..., description="Layer UUID")


class FeatureLayerUpdateBase(LayerUpdateBase, GeospatialAttributes):
    """Base model for feature layer updates."""

    style_id: Optional[UUID] = Field(None, description="Style ID of the layer")
    size: Optional[int] = Field(None, description="Size of the layer in bytes")


class LayerProjectAttributesBase(BaseModel):
    """Base model for the additional attributes of layers in a project."""

    active: bool = Field(
        ...,
        description="Layer is active or not in the project",
    )
    data_source_name: str = Field(
        ...,
        description="Data source name",
    )


class FeatureLayerProjectBase(FeatureLayerBase, LayerProjectAttributesBase):
    """Model for feature layer that are in projects."""

    id: UUID = Field(..., description="Layer UUID")
    style_id: UUID = Field(
        ...,
        description="Style ID of the layer",
    )
    active_style_rule: List[bool] = Field(
        ...,
        description="Array with the active style rules for the respective style in the style",
    )
    query: Optional[str] = Field(None, description="Query to filter the layer data")


# Feature Layer Standard
class FeatureLayerStandardCreate(FeatureLayerBase):
    pass


class FeatureLayerStandardRead(FeatureLayerReadBase):
    pass


class FeatureLayerStandardUpdate(FeatureLayerUpdateBase):
    pass


class FeatureLayerStandardProject(FeatureLayerProjectBase):
    pass


# Feature Layer Indicator
class FeatureLayerIndicatorAttributesBase(BaseModel):
    """Base model for additional attributes feature layer indicator."""

    indicator_type: IndicatorType = Field(..., description="Indicator type")
    payload: dict = Field(..., description="Used Request payload to compute the indicator")
    opportunities: Optional[List[UUID]] = Field(
        None, description="Opportunity data sets that are used to intersect with the indicator"
    )


class FeatureLayerIndicatorCreate(FeatureLayerBase, FeatureLayerIndicatorAttributesBase):
    """Model to create feature layer indicator."""

    pass


class FeatureLayerIndicatorRead(FeatureLayerReadBase, FeatureLayerIndicatorAttributesBase):
    """Model to read a feature layer indicator."""

    pass


class FeatureLayerIndicatorUpdate(FeatureLayerUpdateBase):
    """Model to update a feature layer indicator."""

    payload: Optional[dict] = Field(
        None, description="Used Request payload to compute the indicator"
    )
    opportunities: Optional[List[UUID]] = Field(
        None, description="Opportunity data sets that are used to intersect with the indicator"
    )


class FeatureLayerIndicatorProject(FeatureLayerProjectBase, FeatureLayerIndicatorAttributesBase):
    """Model for feature layer indicator in a project."""

    pass


# Feature Layer Opportunity
class FeatureLayerOpportunityAttributesBase(BaseModel):
    """Base model for feature layer opportunity."""

    scenario_id: Optional[int] = Field(
        None, description="Scenario ID if there is a scenario associated with this layer"
    )


class FeatureLayerOpportunityCreate(FeatureLayerBase, FeatureLayerOpportunityAttributesBase):
    pass


class FeatureLayerOpportunityRead(FeatureLayerReadBase, FeatureLayerOpportunityAttributesBase):
    pass


class FeatureLayerOpportunityUpdate(FeatureLayerUpdateBase, FeatureLayerOpportunityAttributesBase):
    pass


class FeatureLayerOpportunityProject(
    FeatureLayerProjectBase, FeatureLayerOpportunityAttributesBase
):
    pass


# Feature Layer Scenario
class FeatureLayerScenarioAttributesBase(BaseModel):
    """Base model for additional attributes feature layer scenario."""

    scenario_id: int = Field(..., description="Scenario ID of the scenario layer.")
    scenario_type: ScenarioType = Field(..., description="Scenario type")


class FeatureLayerScenarioCreate(FeatureLayerBase, FeatureLayerScenarioAttributesBase):
    """Model to create feature layer scenario."""

    pass


class FeatureLayerScenarioRead(FeatureLayerReadBase, FeatureLayerScenarioAttributesBase):
    """Model to read a feature layer scenario."""

    pass


class FeatureLayerScenarioUpdate(FeatureLayerUpdateBase):
    """Model to update a feature layer scenario."""

    pass


# Feature Layer Analysis Unit
class FeatureLayerAnalysisUnitCreate(FeatureLayerBase):
    pass


class FeatureLayerAnalysisUnitRead(FeatureLayerReadBase):
    pass


class FeatureLayerAnalysisUnitUpdate(FeatureLayerUpdateBase):
    pass


class FeatureLayerAnalysisUnitProject(FeatureLayerProjectBase):
    pass


################################################################################
# Imagery Layer DTOs
################################################################################


class ImageryLayerAttributesBase(BaseModel):
    """Base model for additional attributes imagery layer."""

    url: str = Field(..., description="Layer URL")
    data_type: ImageryLayerDataType = Field(..., description="Content data type")
    legend_urls: List[str] = Field(..., description="Layer legend URLs")


class ImageryLayerCreate(LayerBase, GeospatialAttributes, ImageryLayerAttributesBase):
    """Model to create a imagery layer."""

    pass


class ImageryLayerRead(LayerBase, GeospatialAttributes, ImageryLayerAttributesBase):
    """Model to read a imagery layer."""

    id: UUID = Field(..., description="Layer UUID")


class ImageryLayerUpdate(LayerUpdateBase):
    """Model to"""

    url: Optional[str] = Field(None, description="Layer URL")
    legend_urls: Optional[List[str]] = Field(None, description="Layer legend URLs")


class ImageryLayerProject(LayerBase, ImageryLayerAttributesBase, LayerProjectAttributesBase):
    """Model for imagery layer in a project."""

    id: UUID = Field(..., description="Layer UUID")


################################################################################
# Tile Layer DTOs
################################################################################


class TileLayerAttributesBase(BaseModel):
    """Base model for additional attributes tile layer."""

    url: str = Field(..., description="Layer URL")
    data_type: TileLayerDataType = Field(..., description="Content data type")


class TileLayerCreate(LayerBase, GeospatialAttributes, TileLayerAttributesBase):
    """Model to create a tile layer."""

    pass


class TileLayerRead(LayerBase, GeospatialAttributes, TileLayerAttributesBase):
    """Model to read a tile layer."""

    id: UUID = Field(..., description="Layer UUID")


class TileLayerUpdate(LayerUpdateBase):
    """Model to update a tile layer."""

    url: Optional[str] = Field(None, description="Layer URL")


class TileLayerProject(LayerBase, TileLayerAttributesBase, LayerProjectAttributesBase):
    """Model for tile layer in a project."""

    id: UUID = Field(..., description="Layer UUID")


################################################################################
# Table Layer DTOs
################################################################################


class TableLayerCreate(LayerBase):
    pass


class TableLayerRead(LayerBase):
    id: UUID = Field(..., description="Layer UUID")


class TableLayerUpdate(LayerUpdateBase):
    pass


class TableLayerProject(LayerBase, LayerProjectAttributesBase):
    id: UUID = Field(..., description="Layer UUID")
