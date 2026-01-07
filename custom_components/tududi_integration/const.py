"""Constants for the Tududi HACS integration."""

DOMAIN = "tududi_integration"

# Configuration
CONF_URL = "url"
CONF_TITLE = "title"
CONF_ICON = "icon"
CONF_API_KEY = "api_key"  

# Defaults
DEFAULT_TITLE = "Tududi"
DEFAULT_ICON = "mdi:clipboard-text"

# Sensor constants
SENSOR_UPDATE_INTERVAL = 300  # 5 minutes
SENSOR_TIMEOUT = 30  # 30 seconds

# API Endpoints
API_VERSION = "v1"
API_BASE_PATH = "/api/v1"