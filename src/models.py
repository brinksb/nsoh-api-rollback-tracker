"""Data models for the NSOH API Rollback Tracker."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional


@dataclass
class OverflowRecord:
    """Represents a single storm overflow location's status."""

    location_id: str
    status: int  # 1 = Discharging, 0 = Not discharging, -1 = Offline
    status_start: Optional[int]  # Unix timestamp in milliseconds
    latest_event_start: Optional[int]  # Unix timestamp in milliseconds
    latest_event_end: Optional[int]  # Unix timestamp in milliseconds
    last_updated: Optional[int]  # Unix timestamp in milliseconds
    source: str  # "thames" or "nsoh"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "OverflowRecord":
        return cls(**data)


@dataclass
class RollbackEvent:
    """Represents a detected rollback for a single location."""

    location_id: str
    detected_at: str  # ISO 8601 timestamp
    previous_status_start: Optional[int]  # What NSOH showed before
    current_status_start: Optional[int]  # What NSOH shows now (older = rollback)
    previous_last_updated: Optional[int]
    current_last_updated: Optional[int]
    thames_status_start: Optional[int]  # Thames Water value at detection time
    status_changed: bool  # Did the status value itself change?

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "RollbackEvent":
        return cls(**data)


@dataclass
class ComparisonResult:
    """Result of comparing NSOH snapshots."""

    timestamp: str  # ISO 8601 timestamp
    total_locations: int
    rollbacks_detected: int
    rollback_percentage: float
    is_dataset_level: bool  # True if >50% of locations rolled back
    rollback_events: list[RollbackEvent] = field(default_factory=list)

    def to_dict(self) -> dict:
        result = asdict(self)
        result["rollback_events"] = [e.to_dict() for e in self.rollback_events]
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "ComparisonResult":
        events = [RollbackEvent.from_dict(e) for e in data.get("rollback_events", [])]
        return cls(
            timestamp=data["timestamp"],
            total_locations=data["total_locations"],
            rollbacks_detected=data["rollbacks_detected"],
            rollback_percentage=data["rollback_percentage"],
            is_dataset_level=data["is_dataset_level"],
            rollback_events=events,
        )


@dataclass
class Snapshot:
    """A point-in-time snapshot of API data."""

    timestamp: str  # ISO 8601 timestamp
    source: str  # "thames" or "nsoh"
    records: list[OverflowRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "source": self.source,
            "records": [r.to_dict() for r in self.records],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        records = [OverflowRecord.from_dict(r) for r in data.get("records", [])]
        return cls(
            timestamp=data["timestamp"],
            source=data["source"],
            records=records,
        )

    def get_record_by_id(self, location_id: str) -> Optional[OverflowRecord]:
        """Get a record by location ID."""
        for record in self.records:
            if record.location_id == location_id:
                return record
        return None
