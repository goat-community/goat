"""The published assets a client may fetch through this API.

Two of them, and only two: the **thumbnail** a card shows and the **style** the
map draws a dataset with. Both are small (31 MB and 5.8 MB across the whole
catalog, 27.6 KB and 0.56 KB mean), both are GOAT's own products, and both are
useless to a client that cannot fetch them.

The harmonised GeoParquet is deliberately absent. It has no route, no signed
URL and no private URL: the only reader is this service's own preview, which
range-reads at most 100 features out of an 81 GB prefix. "Not downloadable" is
expressed as "no URL exists", not as a permission check that could be relaxed by
accident.

Three properties worth stating, because each is a decision:

* **The bucket stays private.** Bytes are read with the service's credentials and
  streamed; nothing is signed and no public prefix is opened, so a client never
  learns where the object lives and there is no URL to copy, replay or share.
* **The caller names an item, not an object.** A request is "the thumbnail of
  this dataset". The object key is resolved from that item's own published href,
  so the reachable set is what the harvester pointed at -- not what a caller can
  spell. No request segment is ever concatenated into a key.
* **The kind decides the media type.** A publisher-adjacent `type` field is not
  echoed: it must be one this kind serves, or the request fails. An SVG served
  from our origin with a `text/html` label would be script execution in the
  origin that holds the session.
"""

import logging
import re
import threading
from dataclasses import dataclass
from typing import Any

import duckdb
from goatlib.storage.ducklake import connect_duckdb, load_extensions

from catalog.config import CatalogSettings
from catalog.errors import ApiError
from catalog.services.preview import object_key
from catalog.services.s3_secret import create_s3_secret

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AssetKind:
    """One servable asset: where to find it, and what it may be.

    Adding a kind is a row here -- a precomputed preview (``previews/``,
    ``application/geo+json``) needs no new route.
    """

    #: Path segment a client asks for.
    name: str
    #: Member of the item document's ``assets`` object that points at it.
    asset: str
    #: The only object prefix this kind may read.
    prefix: str
    #: Media types this kind serves. A declared type outside this set is a
    #: refusal rather than something to pass through.
    media_types: frozenset[str]
    #: Served when the publisher declares no type at all.
    default_media_type: str


ASSET_KINDS: dict[str, AssetKind] = {
    "thumbnail": AssetKind(
        name="thumbnail",
        asset="thumbnail",
        prefix="thumbs/",
        # Every one of the catalog's 1,147 thumbnails is an SVG today. The other
        # three are here so a raster thumbnail arrives without a code change --
        # and so `text/html` does not.
        media_types=frozenset(
            {"image/svg+xml", "image/png", "image/jpeg", "image/webp"}
        ),
        default_media_type="image/svg+xml",
    ),
    "style": AssetKind(
        name="style",
        asset="style",
        prefix="styles/",
        media_types=frozenset({"application/json"}),
        default_media_type="application/json",
    ),
}

#: What an item id may look like. Not a UUID pattern: real ids carry a source
#: prefix and a colon (``data_gv_at:2f5baa1f-208c-42c2-8d…``). This is a shape
#: check on the way in, not the authorisation -- the id still has to resolve to
#: an item in the mirror, and the key still comes from that item's own href.
_ITEM_ID = re.compile(r"^[A-Za-z0-9._:-]{1,200}$")


def valid_item_id(item_id: str) -> bool:
    return bool(_ITEM_ID.match(item_id))


class AssetReader:
    """Reads asset objects out of the catalog bucket.

    One connection, held for the process, carrying the bucket credentials --
    the same arrangement as the preview reader and for the same reason: the
    store's connection is swapped on every mirror reload and only ever reads
    local files.

    DuckDB rather than an S3 client because it is already a dependency and
    already knows how to authenticate against the bucket. The cost is that a
    read is whole-object, which is why :attr:`CatalogSettings.assets_max_bytes`
    exists and why this serves only the two small prefixes.
    """

    def __init__(self, settings: CatalogSettings) -> None:
        self._settings = settings
        self._con: duckdb.DuckDBPyConnection | None = None
        self._lock = threading.Lock()

    def _connect(self) -> duckdb.DuckDBPyConnection:
        with self._lock:
            if self._con is not None:
                return self._con
            con = connect_duckdb()
            load_extensions(con, "httpfs")
            # One-shot reads: DuckDB would otherwise keep each S3 object read
            # in memory for the life of this connection.
            con.execute("SET enable_external_file_cache=false")
            create_s3_secret(con, "catalog_assets", self._settings)
            self._con = con
            return con

    def object_url(self, key: str) -> str:
        """The readable URL of one object.

        A seam, not indirection: it is the only part of the read that needs a
        bucket, so a test can point the same code at a local file.
        """
        return f"s3://{self._settings.s3_catalog_bucket or ''}/{key}"

    def media_type(self, kind: AssetKind, declared: object) -> str:
        """The type to serve, from what the publisher declared.

        Outside the kind's set is a refusal: this body is served from the same
        origin as the app, so honouring an arbitrary label is how a thumbnail
        becomes a script.
        """
        if declared is None:
            return kind.default_media_type
        value = str(declared).split(";")[0].strip().lower()
        if value not in kind.media_types:
            raise ApiError(404, f"{kind.name} is not a servable media type")
        return value

    def read(self, kind: AssetKind, row: dict[str, Any]) -> tuple[bytes, str, str]:
        """``(bytes, media type, object key)`` for one item's asset.

        404 for every way this can fail to be a servable asset -- the item does
        not carry one, the href points outside the kind's prefix, the object is
        missing, the declared type is not one we serve. From a client's side
        they are one answer: this dataset has no such asset here.
        """
        assets = row.get("assets")
        asset = assets.get(kind.asset) if isinstance(assets, dict) else None
        href = asset.get("href") if isinstance(asset, dict) else None
        if not href:
            raise ApiError(404, f"item has no {kind.name}")

        key = object_key(
            str(href), self._settings.s3_catalog_bucket or "", prefixes=(kind.prefix,)
        )
        media_type = self.media_type(
            kind, asset.get("type") if isinstance(asset, dict) else None
        )

        url = self.object_url(key)
        # A cursor per call, never the shared connection: the reader serves
        # concurrent threadpool requests, and a DuckDB connection is not safe to
        # execute on from two threads at once — one request's fetch can return
        # another request's rows, i.e. item A's thumbnail under item B's URL.
        cursor = self._connect().cursor()
        try:
            rows = cursor.execute("SELECT content FROM read_blob(?)", [url]).fetchall()
        except duckdb.Error as exc:
            # The object is named by a published href, so a miss is upstream
            # drift (an href pointing at something that was never uploaded)
            # rather than a client error worth a 500.
            logger.warning("asset read failed for %s: %s", key, exc)
            raise ApiError(404, f"{kind.name} is not available") from exc
        finally:
            cursor.close()

        if not rows or rows[0][0] is None:
            raise ApiError(404, f"{kind.name} is not available")
        content = bytes(rows[0][0])
        if len(content) > self._settings.assets_max_bytes:
            # A read is whole-object, so the ceiling is the only thing standing
            # between one malformed object and the pod's memory.
            logger.warning(
                "asset %s is %d bytes, over the %d ceiling",
                key,
                len(content),
                self._settings.assets_max_bytes,
            )
            raise ApiError(404, f"{kind.name} is not available")
        return content, media_type, key
