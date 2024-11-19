from enum import Enum


class ProcessingStatus(str, Enum):
    """Pocessing status schema."""

    in_progress = "in_progress"  # Catchment area computation is in progress
    success = "success"  # Catchment area computation was successful
    failure = "failure"  # Catchment area computation failed, reason unknown
    disconnected_origin = "disconnected_origin"  # Starting point(s) are not connected to the street network
