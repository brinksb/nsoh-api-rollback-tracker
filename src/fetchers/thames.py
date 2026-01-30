"""Thames Water API client for fetching discharge status data."""

import time
from datetime import datetime, timezone
from typing import Optional

import requests

from ..config import (
    THAMES_WATER_API_URL,
    THAMES_STATUS_MAP,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
)
from ..models import OverflowRecord, Snapshot


def parse_iso_timestamp(iso_string: Optional[str]) -> Optional[int]:
    """Convert ISO 8601 timestamp to Unix milliseconds."""
    if not iso_string:
        return None
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1000)
    except (ValueError, AttributeError):
        return None


def parse_status(status_string: Optional[str]) -> int:
    """Convert Thames Water status string to integer."""
    if not status_string:
        return -1  # Treat unknown as offline
    return THAMES_STATUS_MAP.get(status_string, -1)


def fetch_thames_water_data() -> Snapshot:
    """Fetch current discharge status from Thames Water API.

    Returns:
        Snapshot containing all overflow records.

    Raises:
        requests.RequestException: If the API request fails after retries.
    """
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                THAMES_WATER_API_URL,
                timeout=REQUEST_TIMEOUT,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            data = response.json()
            break
        except requests.RequestException as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    else:
        raise last_exception

    timestamp = datetime.now(timezone.utc).isoformat()
    records = []

    items = data.get("items", [])
    for item in items:
        record = OverflowRecord(
            location_id=item.get("uniqueId", ""),
            status=parse_status(item.get("alertStatus")),
            status_start=parse_iso_timestamp(item.get("statusChanged")),
            latest_event_start=parse_iso_timestamp(
                item.get("mostRecentDischargeAlertStart")
            ),
            latest_event_end=parse_iso_timestamp(
                item.get("mostRecentDischargeAlertStop")
            ),
            last_updated=parse_iso_timestamp(item.get("statusChanged")),
            source="thames",
        )
        if record.location_id:
            records.append(record)

    return Snapshot(timestamp=timestamp, source="thames", records=records)
