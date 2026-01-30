"""Main entry point for the NSOH API Rollback Tracker."""

import sys
from datetime import datetime, timezone

from .fetchers.thames import fetch_thames_water_data
from .fetchers.nsoh import fetch_nsoh_data
from .detector import detect_rollbacks
from .storage import (
    save_snapshot,
    save_latest,
    load_latest,
    append_rollback_log,
    save_latest_comparison,
)


def main() -> int:
    """Run the rollback detection cycle.

    Returns:
        0 if no rollbacks detected, 1 if rollbacks detected.
    """
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting rollback detection cycle...")

    # Fetch data from both APIs
    print("Fetching Thames Water data...")
    try:
        thames_snapshot = fetch_thames_water_data()
        print(f"  Retrieved {len(thames_snapshot.records)} records")
    except Exception as e:
        print(f"  ERROR: Failed to fetch Thames Water data: {e}")
        return 2

    print("Fetching NSOH data...")
    try:
        nsoh_snapshot = fetch_nsoh_data()
        print(f"  Retrieved {len(nsoh_snapshot.records)} records")
    except Exception as e:
        print(f"  ERROR: Failed to fetch NSOH data: {e}")
        return 2

    # Load previous NSOH snapshot for comparison
    previous_nsoh = load_latest("nsoh")

    if previous_nsoh is None:
        print("No previous NSOH snapshot found. Saving baseline...")
        save_snapshot(thames_snapshot)
        save_snapshot(nsoh_snapshot)
        save_latest(thames_snapshot)
        save_latest(nsoh_snapshot)
        print("Baseline saved. Run again to detect rollbacks.")
        return 0

    # Detect rollbacks
    print("Comparing snapshots...")
    result = detect_rollbacks(
        previous_nsoh=previous_nsoh,
        current_nsoh=nsoh_snapshot,
        current_thames=thames_snapshot,
    )

    # Save current snapshots
    save_snapshot(thames_snapshot)
    save_snapshot(nsoh_snapshot)
    save_latest(thames_snapshot)
    save_latest(nsoh_snapshot)

    # Save comparison result
    save_latest_comparison(result)

    if result.rollbacks_detected > 0:
        append_rollback_log(result)
        pattern = "DATASET-LEVEL" if result.is_dataset_level else "ROW-LEVEL"
        print(f"\n{'='*60}")
        print(f"ROLLBACK DETECTED! ({pattern})")
        print(f"  Affected: {result.rollbacks_detected}/{result.total_locations} locations ({result.rollback_percentage}%)")
        print(f"  Timestamp: {result.timestamp}")
        print(f"{'='*60}\n")
        return 1
    else:
        print(f"No rollbacks detected. {result.total_locations} locations checked.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
