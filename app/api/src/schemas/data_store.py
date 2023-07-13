from typing import TYPE_CHECKING
from enum import Enum
from src.db.models.data_store import DataStoreBase, DataStore

class DataStoreType(str, Enum):
    """Data store type."""

    postgis = "postgis"
    external = "external"

class DataStoreCreate(DataStoreBase):
    pass

class DataStoreUpdate(DataStoreBase):
    pass

class DataStoreRead(DataStore):
    pass