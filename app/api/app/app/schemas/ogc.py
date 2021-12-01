# MIT License

# Copyright (c) 2020 Development Seed

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

"""OGC: Open GeoSpatial Consortium models."""


from typing import List

from pydantic import AnyHttpUrl, BaseModel

from app.resources.enums import MimeTypes


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
