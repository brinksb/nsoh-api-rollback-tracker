# NSOH API Rollback Tracker

Detects data rollbacks in the National Storm Overflow Hub (NSOH). Thames Water publishes storm overflow event data to NSOH, but the published data sometimes reverts to previous readings. This tool compares snapshots over time to identify when rollbacks occur.

## How It Works

1. **Fetches data** from both Thames Water API and NSOH ArcGIS FeatureServer every 5 minutes
2. **Compares** the current NSOH snapshot against the previous snapshot
3. **Detects rollbacks** when timestamps go backwards (current < previous)
4. **Logs rollbacks** with full context including Thames Water data at detection time
5. **Dashboard** displays rollback history and summary statistics

### Rollback Types

- **Dataset-level**: >50% of locations roll back simultaneously (likely cache/ingestion issue)
- **Row-level**: Individual locations roll back independently

## Quick Start

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tracker
python -m src.main
```

First run captures a baseline. Subsequent runs detect rollbacks by comparing to the previous snapshot.

### Automated (GitHub Actions)

1. Push this repository to GitHub
2. Enable GitHub Actions (Settings → Actions → Allow all actions)
3. Enable GitHub Pages (Settings → Pages → Source: Deploy from branch, Branch: main, Folder: /docs)
4. The tracker runs automatically every 5 minutes

## Project Structure

```
├── .github/workflows/
│   └── tracker.yml           # GitHub Actions (5-min cron)
├── src/
│   ├── config.py             # API URLs, constants
│   ├── fetchers/
│   │   ├── thames.py         # Thames Water API client
│   │   └── nsoh.py           # NSOH ArcGIS client
│   ├── models.py             # Data models
│   ├── detector.py           # Rollback detection logic
│   ├── storage.py            # JSON file management
│   └── main.py               # Entry point
├── data/
│   ├── snapshots/            # Timestamped snapshots by date
│   ├── rollbacks/            # rollback_log.json, latest_comparison.json
│   └── latest/               # Current state for comparison
├── docs/                     # GitHub Pages dashboard
└── requirements.txt
```

## Data Sources

### Thames Water API (Source of Truth)
```
https://api.thameswater.co.uk/opendata/v2/discharge/status
```
- JSON format with `items` array
- Status values: `"Discharging"`, `"Not discharging"`, `"Offline"`

### NSOH ArcGIS FeatureServer
```
https://services2.arcgis.com/g6o32ZDQ33GpCIu3/arcgis/rest/services/Thames_Water_Storm_Overflow_Activity_(Production)_view/FeatureServer/0/query
```
- ArcGIS JSON with `features` array
- Status values: `1` (Discharging), `0` (Not discharging), `-1` (Offline)

## Exit Codes

- `0`: Success, no rollbacks detected
- `1`: Rollbacks detected
- `2`: Error (API failure, etc.)
