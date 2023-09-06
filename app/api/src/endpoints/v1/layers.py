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

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path as directoryPath
from typing import Any, Callable, Dict, List, Optional, Type
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from morecantile import Tile, TileMatrixSet, tms
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.requests import Request
from starlette.responses import HTMLResponse, Response
from starlette.routing import NoMatchFound
from starlette.templating import Jinja2Templates

from src.core.config import settings
from src.crud.legacy.crud_layer import layer as crud_layer
from src.db import models
from src.endpoints.legacy import deps
from src.resources import tms as custom_tms
from src.resources.enums import MimeTypes
from src.schemas.layer import (
    TileMatrixSetList,
    VectorTileFunction,
    VectorTileLayer,
    VectorTileTable,
)
from src.schemas.layer import registry as FunctionRegistry
from src.schemas.mapbox import TileJSON

try:
    pass  # type: ignore
except ImportError:
    # Try backported to PY<39 `importlib_resources`.
    pass  # type: ignore

templates = Jinja2Templates(directory=directoryPath(settings.LAYER_TEMPLATES_DIR))  # type: ignore


TILE_RESPONSE_PARAMS: Dict[str, Any] = {
    "responses": {200: {"content": {"application/x-protobuf": {}}}},
    "response_class": Response,
}

# Register Custom TMS
tms = tms.register([custom_tms.EPSG3413, custom_tms.EPSG6933])

TileMatrixSetNames = Enum(  # type: ignore
    "TileMatrixSetNames", [(a, a) for a in sorted(tms.list())]
)


def TileParams(
    z: int = Path(..., ge=0, le=30, description="Tiles's zoom level"),
    x: int = Path(..., description="Tiles's column"),
    y: int = Path(..., description="Tiles's row"),
) -> Tile:
    """Tile parameters."""
    return Tile(x, y, z)


def TileMatrixSetParams(
    TileMatrixSetId: TileMatrixSetNames = Query(
        TileMatrixSetNames.WebMercatorQuad,  # type: ignore
        description="TileMatrixSet Name (default: 'WebMercatorQuad')",
    ),
) -> TileMatrixSet:
    """TileMatrixSet parameters."""
    return tms.get(TileMatrixSetId.name)


def LayerParams(
    request: Request,
    layer: str = Path(..., description="Layer Name"),
) -> VectorTileLayer:
    """Return Layer Object."""

    if layer == "building":
        layer = "basic.building"
    else:
        layer = "extra." + layer

    for r in request.app.state.table_catalog:
        if r["id"] == layer:
            return VectorTileTable(**r)

    raise HTTPException(status_code=404, detail=f"Table/Function '{layer}' not found.")


@dataclass
class VectorTilerFactory:
    """VectorTiler Factory."""

    # FastAPI router
    router: APIRouter = field(default_factory=APIRouter)

    # Enum of supported TMS
    supported_tms: Type[TileMatrixSetNames] = TileMatrixSetNames
    # TileMatrixSet dependency
    tms_dependency: Callable[..., TileMatrixSet] = TileMatrixSetParams

    # Table/Function dependency
    layer_dependency: Callable[..., VectorTileLayer] = LayerParams

    with_tables_metadata: bool = False
    with_functions_metadata: bool = False
    with_viewer: bool = False
    # Router Prefix is needed to find the path for routes when prefixed
    # e.g if you mount the route with `/foo` prefix, router_prefix foo is injected
    router_prefix: str = ""

    def __post_init__(self):
        """Post Init: register route and configure specific options."""
        self.register_routes()
        self.router_prefix = settings.API_V2_STR + self.router_prefix

    def register_routes(self):
        """Register Routes."""
        self.register_tiles()
        self.register_tiles_matrix_sets()

        if self.with_tables_metadata:
            self.register_tables_metadata()

        if self.with_functions_metadata:
            self.register_functions_metadata()

        if self.with_viewer:
            self.register_viewer()

    def url_for(self, request: Request, name: str, **path_params: Any) -> str:
        """Return full url (with prefix) for a specific endpoint."""
        url_path = self.router.url_path_for(name, **path_params)
        base_url = str(request.base_url)
        if self.router_prefix:
            base_url += self.router_prefix.lstrip("/")
        return url_path.make_absolute_url(base_url=base_url)

    def register_tiles(self):
        """Register /tiles endpoints."""

        @self.router.get(r"/{layer}/{z}/{x}/{y}.pbf", **TILE_RESPONSE_PARAMS)
        @self.router.get(r"/{TileMatrixSetId}/{layer}/{z}/{x}/{y}.pbf", **TILE_RESPONSE_PARAMS)
        async def tile(
            *,
            db: AsyncSession = Depends(deps.get_db),
            request: Request,
            tile: Tile = Depends(TileParams),
            tms: TileMatrixSet = Depends(self.tms_dependency),
            layer=Depends(self.layer_dependency),
            current_user: models.User = Depends(deps.get_current_active_user),
        ):
            """Return vector tile."""
            qs_key_to_remove = ["tilematrixsetid"]
            kwargs = {
                key: value
                    for (key, value) in request.query_params._list
                    if key.lower() not in qs_key_to_remove
            }

            content = await crud_layer.tile_from_table(db, tile, tms, layer, **kwargs)
            return Response(bytes(content), media_type=MimeTypes.pbf.value)

        @self.router.get(
            r"/{layer}/tilejson.json",
            response_model=TileJSON,
            responses={200: {"description": "Return a tilejson"}},
            response_model_exclude_none=True,
        )
        @self.router.get(
            r"/{TileMatrixSetId}/{layer}/tilejson.json",
            response_model=TileJSON,
            responses={200: {"description": "Return a tilejson"}},
            response_model_exclude_none=True,
        )
        async def tilejson(
            request: Request,
            layer=Depends(self.layer_dependency),
            tms: TileMatrixSet = Depends(self.tms_dependency),
            minzoom: Optional[int] = Query(None, description="Overwrite default minzoom."),
            maxzoom: Optional[int] = Query(None, description="Overwrite default maxzoom."),
            current_user: models.User = Depends(deps.get_current_active_user),
        ):
            """Return TileJSON document."""
            path_params: Dict[str, Any] = {
                "TileMatrixSetId": tms.identifier,
                "layer": layer.id,
                "z": "{z}",
                "x": "{x}",
                "y": "{y}",
            }
            tile_endpoint = self.url_for(request, "tile", **path_params)
            qs_key_to_remove = ["tilematrixsetid", "minzoom", "maxzoom"]
            query_params = {
                key: value
                    for (key, value) in request.query_params._list
                    if key.lower() not in qs_key_to_remove
            }

            if query_params:
                tile_endpoint += f"?{urlencode(query_params)}"

            minzoom = minzoom if minzoom is not None else (layer.minzoom or tms.minzoom)
            maxzoom = maxzoom if maxzoom is not None else (layer.maxzoom or tms.maxzoom)

            return {
                "minzoom": minzoom,
                "maxzoom": maxzoom,
                "name": layer.id,
                "bounds": layer.bounds,
                "tiles": [tile_endpoint],
            }

    def register_tiles_matrix_sets(self):
        @self.router.get(
            r"/tileMatrixSets",
            response_model=TileMatrixSetList,
            response_model_exclude_none=True,
        )
        async def TileMatrixSet_list(
            request: Request, current_user: models.User = Depends(deps.get_current_active_user)
        ):
            """
            Return list of supported TileMatrixSets.

            Specs: http://docs.opengeospatial.org/per/19-069.html#_tilematrixsets
            """
            return {
                "tileMatrixSets": [
                    {
                        "id": tms.name,
                        "title": tms.name,
                        "links": [
                            {
                                "href": self.url_for(
                                    request,
                                    "TileMatrixSet_info",
                                    TileMatrixSetId=tms.name,
                                ),
                                "rel": "item",
                                "type": "application/json",
                            }
                        ],
                    }
                    for tms in self.supported_tms
                ]
            }

        @self.router.get(
            r"/tileMatrixSets/{TileMatrixSetId}",
            response_model=TileMatrixSet,
            response_model_exclude_none=True,
        )
        async def TileMatrixSet_info(
            tms: TileMatrixSet = Depends(self.tms_dependency),
            current_user: models.User = Depends(deps.get_current_active_user),
        ):
            """Return TileMatrixSet JSON document."""
            return tms

    def register_tables_metadata(self):
        """Register metadata endpoints."""

        @self.router.get(
            r"/tables.json",
            response_model=List[VectorTileTable],
            response_model_exclude_none=True,
        )
        async def tables_index(
            request: Request, current_user: models.User = Depends(deps.get_current_active_user)
        ):
            """Index of tables."""

            def _get_tiles_url(id) -> str:
                try:
                    return self.url_for(request, "tile", layer=id, z="{z}", x="{x}", y="{y}")
                except NoMatchFound:
                    return None

            return [
                VectorTileTable(**r, tileurl=_get_tiles_url(r["id"]))
                for r in request.app.state.table_catalog
            ]

        @self.router.get(
            r"/table/{layer}.json",
            response_model=VectorTileTable,
            responses={200: {"description": "Return table metadata"}},
            response_model_exclude_none=True,
        )
        async def table_metadata(
            request: Request,
            layer=Depends(self.layer_dependency),
            current_user: models.User = Depends(deps.get_current_active_user),
        ):
            """Return table metadata."""

            def _get_tiles_url(id) -> str:
                try:
                    return self.url_for(request, "tile", layer=id, z="{z}", x="{x}", y="{y}")
                except NoMatchFound:
                    return None

            layer.tileurl = _get_tiles_url(layer.id)
            return layer

    def register_functions_metadata(self):  # noqa
        """Register function metadata endpoints."""

        @self.router.get(
            r"/functions.json",
            response_model=List[VectorTileFunction],
            response_model_exclude_none=True,
            response_model_exclude={"sql"},
        )
        async def functions_index(request: Request):
            """Index of functions."""

            def _get_tiles_url(id) -> str:
                try:
                    return self.url_for(request, "tile", layer=id, z="{z}", x="{x}", y="{y}")
                except NoMatchFound:
                    return None

            return [
                VectorTileFunction(**func.dict(exclude_none=True), tileurl=_get_tiles_url(id))
                for id, func in FunctionRegistry.funcs.items()
            ]

        @self.router.get(
            r"/function/{layer}.json",
            response_model=VectorTileFunction,
            responses={200: {"description": "Return Function metadata"}},
            response_model_exclude_none=True,
            response_model_exclude={"sql"},
        )
        async def function_metadata(
            request: Request,
            layer=Depends(self.layer_dependency),
            current_user: models.User = Depends(deps.get_current_active_user),
        ):
            """Return table metadata."""

            def _get_tiles_url(id) -> str:
                try:
                    return self.url_for(request, "tile", layer=id, z="{z}", x="{x}", y="{y}")
                except NoMatchFound:
                    return None

            layer.tileurl = _get_tiles_url(layer.id)
            return layer

    def register_viewer(self):
        """Register viewer."""

        @self.router.get(
            r"/list",
            response_class=HTMLResponse,
        )
        async def list_layers(
            request: Request, current_user: models.User = Depends(deps.get_current_active_user)
        ):
            """Display layer list."""
            return templates.TemplateResponse(
                name="index.html",
                context={"index": request.app.state.table_catalog, "request": request},
                media_type="text/html",
            )

        @self.router.get(
            r"/{layer}/viewer",
            response_class=HTMLResponse,
        )
        async def demo(
            request: Request,
            layer=Depends(LayerParams),
            current_user: models.User = Depends(deps.get_current_active_user),
        ):
            """Demo for each table."""
            tile_url = self.url_for(request, "tilejson", layer=layer.id)
            return templates.TemplateResponse(
                name="viewer.html",
                context={"endpoint": tile_url, "request": request, "bounds": layer.bounds},
                media_type="text/html",
            )
