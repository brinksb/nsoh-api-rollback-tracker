"""NSOH ArcGIS FeatureServer client for fetching storm overflow data."""

import time
from datetime import datetime, timezone
from typing import Optional

import requests

from ..config import (
    NSOH_ARCGIS_URL,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    ARCGIS_PAGE_SIZE,
)
from ..models import OverflowRecord, Snapshot


def fetch_nsoh_page(offset: int = 0) -> dict:
    """Fetch a single page of NSOH data.

    Args:
        offset: Record offset for pagination.

    Returns:
        Raw JSON response from the API.

    Raises:
        requests.RequestException: If the API request fails after retries.
    """
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "json",
        "resultOffset": offset,
        "resultRecordCount": ARCGIS_PAGE_SIZE,
    }

    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(
                NSOH_ARCGIS_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)

    raise last_exception


def parse_feature(feature: dict) -> Optional[OverflowRecord]:
    """Parse an ArcGIS feature into an OverflowRecord.

    Args:
        feature: Raw feature from ArcGIS response.

    Returns:
        OverflowRecord or None if parsing fails.
    """
    attrs = feature.get("attributes", {})
    location_id = attrs.get("Id")

    if not location_id:
        return None

    return OverflowRecord(
        location_id=location_id,
        status=attrs.get("Status", -1),
        status_start=attrs.get("StatusStart"),
        latest_event_start=attrs.get("LatestEventStart"),
        latest_event_end=attrs.get("LatestEventEnd"),
        last_updated=attrs.get("LastUpdated"),
        source="nsoh",
    )


def fetch_nsoh_data() -> Snapshot:
    """Fetch all current data from NSOH ArcGIS FeatureServer.

    Handles pagination to retrieve all records.

    Returns:
        Snapshot containing all overflow records.

    Raises:
        requests.RequestException: If the API request fails after retries.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    records = []
    offset = 0

    while True:
        data = fetch_nsoh_page(offset)
        features = data.get("features", [])

        if not features:
            break

        for feature in features:
            record = parse_feature(feature)
            if record:
                records.append(record)

        # Check if there are more records
        if len(features) < ARCGIS_PAGE_SIZE:
            break

        offset += ARCGIS_PAGE_SIZE

    return Snapshot(timestamp=timestamp, source="nsoh", records=records)
