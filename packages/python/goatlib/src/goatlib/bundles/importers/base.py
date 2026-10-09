"""Generic bundle import framework.

An importer turns an uploaded source (a GTFS zip, an OSM extract, …) into a set
of member layers for a bundle of a given type. The framework is
spec-driven: which roles are required comes from
``goatlib.models.bundle.SPECS``; how a source maps onto those roles is
the per-type importer's job. Register one importer per
``BundleTypeName`` and the runner/endpoints stay type-agnostic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Tuple

from pydantic import BaseModel

from goatlib.models.bundle import (
    BundleTypeName,
    BundleTypeSpec,
    get_spec,
)

#: Memory one DuckDB connection of an import may use before spilling to disk.
#: Several run in the same worker process during an import, alongside builds
#: that hold memory DuckDB does not account for (a PT timetable, a street
#: graph), so each gets a fixed share rather than DuckDB's default of most of
#: the machine. Same budget as the Overture writer's sort.
DUCKDB_MEMORY_LIMIT = "1GB"


def bound_duckdb(con: Any, spill_dir: str) -> Any:
    """Bound ``con`` to ``DUCKDB_MEMORY_LIMIT``, spilling into ``spill_dir``.
    Returns the connection, so a fresh one can be bounded where it is made."""
    con.execute(f"SET memory_limit='{DUCKDB_MEMORY_LIMIT}'")
    con.execute("SET temp_directory='" + spill_dir.replace("'", "''") + "'")
    return con


LayerKind = Literal["feature", "table"]
GeometryType = Literal["point", "line", "polygon"]


class ExtractedLayer(BaseModel):
    """One member layer produced from the source, ready to be ingested."""

    role: str
    name: str
    layer_type: LayerKind
    geometry_type: Optional[GeometryType] = None
    # Local file the runner ingests into DuckLake: parquet as is, anything else
    # through IOConverter first.
    file_path: str


class ValidationResult(BaseModel):
    """Outcome of validating a source against a bundle type's spec."""

    valid: bool
    detected_roles: List[str] = []
    missing_required_roles: List[str] = []
    errors: List[str] = []


class BundleMetadata(BaseModel):
    """Dataset-level provenance a source states about itself.

    Only what the source asserts: a field left None is written as nothing
    rather than guessed. License, attribution and lineage are deliberately
    absent — no source states them in a form that can be trusted without a
    human, so they stay for the owner to author.
    """

    distributor_name: Optional[str] = None
    distributor_email: Optional[str] = None
    distribution_url: Optional[str] = None
    data_reference_year: Optional[int] = None

    def stated(self) -> dict:
        """The fields the source actually stated, ready to persist."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class BundleImporter(ABC):
    """Base class for per-type importers."""

    #: The bundle type this importer handles.
    bundle_type: BundleTypeName
    #: Lower-case file suffixes this importer accepts, e.g. (".zip",).
    accepted_extensions: Tuple[str, ...] = ()

    @property
    def spec(self) -> BundleTypeSpec:
        return get_spec(self.bundle_type)

    def matches_filename(self, filename: str) -> bool:
        """Whether a file *name* looks like a source for this type.

        Extension-based by default; override where the extension alone is
        ambiguous. Only routes the upload — ``validate`` decides usability.
        """
        lower = filename.lower()
        return any(lower.endswith(ext) for ext in self.accepted_extensions)

    def matches_source(self, source_path: str) -> bool:
        """Whether a file's *contents* identify it as a source for this type.

        The fallback for when the name says nothing. Default is no, so a type
        opts in only if it can sniff cheaply.
        """
        return False

    @abstractmethod
    def validate(self, source_path: str) -> ValidationResult:
        """Cheaply check the source against the type's spec (required roles
        present, key columns) — no full extraction. Safe to call synchronously."""

    @abstractmethod
    def extract_layers(self, source_path: str, workdir: str) -> List[ExtractedLayer]:
        """Produce the member layers' local files under ``workdir``. Assumes the
        source already validated."""

    def extract_metadata(self, source_path: str) -> BundleMetadata:
        """Provenance the source states about itself. Empty by default: a format
        that carries no such declaration contributes nothing rather than a
        plausible-looking guess."""
        return BundleMetadata()


_REGISTRY: Dict[BundleTypeName, BundleImporter] = {}


def register_importer(importer: BundleImporter) -> BundleImporter:
    _REGISTRY[importer.bundle_type] = importer
    return importer


def get_importer(
    bundle_type: "BundleTypeName | str",
) -> BundleImporter:
    """Return the importer for a bundle type (raises if none registered)."""
    key = BundleTypeName(bundle_type)
    if key not in _REGISTRY:
        raise ValueError(f"No importer registered for bundle type '{key.value}'")
    return _REGISTRY[key]


def infer_bundle_type(
    filename: str, source_path: Optional[str] = None
) -> Optional[BundleTypeName]:
    """Which bundle type an upload is, or None for a plain single-layer dataset.

    The name is checked first; when it says nothing — and a local copy is
    available — importers get to sniff the contents. Two bundle types now share
    the ``.zip`` extension, so the name alone cannot always decide.

    Registry-driven, so registering an importer is all a new type needs.
    """
    for importer in _REGISTRY.values():
        if importer.matches_filename(filename):
            return importer.bundle_type
    if source_path is not None:
        for importer in _REGISTRY.values():
            if importer.matches_source(source_path):
                return importer.bundle_type
    return None
