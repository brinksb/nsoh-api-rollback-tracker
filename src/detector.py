"""Rollback detection logic for comparing NSOH snapshots."""

from datetime import datetime, timezone
from typing import Optional

from .models import Snapshot, OverflowRecord, RollbackEvent, ComparisonResult


def detect_record_rollback(
    previous: OverflowRecord,
    current: OverflowRecord,
    thames_record: Optional[OverflowRecord],
    detection_time: str,
) -> Optional[RollbackEvent]:
    """Detect if a single record has rolled back.

    A rollback occurs when the current NSOH timestamp is OLDER than
    the previous NSOH timestamp we captured.

    Args:
        previous: Previous NSOH record.
        current: Current NSOH record.
        thames_record: Current Thames Water record for context.
        detection_time: ISO timestamp of detection.

    Returns:
        RollbackEvent if rollback detected, None otherwise.
    """
    # Compare StatusStart timestamps
    prev_status_start = previous.status_start
    curr_status_start = current.status_start

    # Compare LastUpdated as fallback
    prev_last_updated = previous.last_updated
    curr_last_updated = current.last_updated

    rollback_detected = False

    # Check if StatusStart went backwards
    if prev_status_start is not None and curr_status_start is not None:
        if curr_status_start < prev_status_start:
            rollback_detected = True

    # Also check LastUpdated going backwards
    if prev_last_updated is not None and curr_last_updated is not None:
        if curr_last_updated < prev_last_updated:
            rollback_detected = True

    if not rollback_detected:
        return None

    return RollbackEvent(
        location_id=current.location_id,
        detected_at=detection_time,
        previous_status_start=prev_status_start,
        current_status_start=curr_status_start,
        previous_last_updated=prev_last_updated,
        current_last_updated=curr_last_updated,
        thames_status_start=thames_record.status_start if thames_record else None,
        status_changed=previous.status != current.status,
    )


def detect_rollbacks(
    previous_nsoh: Snapshot,
    current_nsoh: Snapshot,
    current_thames: Optional[Snapshot] = None,
) -> ComparisonResult:
    """Compare NSOH snapshots to detect rollbacks.

    Args:
        previous_nsoh: Previous NSOH snapshot.
        current_nsoh: Current NSOH snapshot.
        current_thames: Current Thames Water snapshot for context.

    Returns:
        ComparisonResult with all detected rollbacks.
    """
    detection_time = datetime.now(timezone.utc).isoformat()
    rollback_events = []

    # Build lookup maps
    previous_by_id = {r.location_id: r for r in previous_nsoh.records}
    thames_by_id = {}
    if current_thames:
        thames_by_id = {r.location_id: r for r in current_thames.records}

    # Check each current record against previous
    for current_record in current_nsoh.records:
        location_id = current_record.location_id
        previous_record = previous_by_id.get(location_id)

        if not previous_record:
            # New location, can't detect rollback
            continue

        thames_record = thames_by_id.get(location_id)

        event = detect_record_rollback(
            previous=previous_record,
            current=current_record,
            thames_record=thames_record,
            detection_time=detection_time,
        )

        if event:
            rollback_events.append(event)

    total_locations = len(current_nsoh.records)
    rollbacks_detected = len(rollback_events)

    rollback_percentage = 0.0
    if total_locations > 0:
        rollback_percentage = (rollbacks_detected / total_locations) * 100

    # Dataset-level rollback if more than 50% of locations affected
    is_dataset_level = rollback_percentage > 50

    return ComparisonResult(
        timestamp=detection_time,
        total_locations=total_locations,
        rollbacks_detected=rollbacks_detected,
        rollback_percentage=round(rollback_percentage, 2),
        is_dataset_level=is_dataset_level,
        rollback_events=rollback_events,
    )
