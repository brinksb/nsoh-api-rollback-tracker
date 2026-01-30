"""Configuration constants for the NSOH API Rollback Tracker."""

# API Endpoints
THAMES_WATER_API_URL = "https://api.thameswater.co.uk/opendata/v2/discharge/status"
NSOH_ARCGIS_URL = (
    "https://services2.arcgis.com/g6o32ZDQ33GpCIu3/arcgis/rest/services/"
    "Thames_Water_Storm_Overflow_Activity_(Production)_view/FeatureServer/0/query"
)

# Request settings
REQUEST_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# ArcGIS pagination
ARCGIS_PAGE_SIZE = 1000

# Status mappings
THAMES_STATUS_MAP = {
    "Discharging": 1,
    "Not discharging": 0,
    "Offline": -1,
}

NSOH_STATUS_MAP = {
    1: "Discharging",
    0: "Not discharging",
    -1: "Offline",
}

# Data paths (relative to project root)
DATA_DIR = "data"
SNAPSHOTS_DIR = f"{DATA_DIR}/snapshots"
ROLLBACKS_DIR = f"{DATA_DIR}/rollbacks"
LATEST_DIR = f"{DATA_DIR}/latest"

# File names
ROLLBACK_LOG_FILE = "rollback_log.json"
LATEST_COMPARISON_FILE = "latest_comparison.json"
THAMES_LATEST_FILE = "thames.json"
NSOH_LATEST_FILE = "nsoh.json"
