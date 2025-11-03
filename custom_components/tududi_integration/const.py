"""Constants for the Tududi HACS integration."""

DOMAIN = "tududi_integration"

# Configuration
CONF_URL = "url"
CONF_TITLE = "title"
CONF_ICON = "icon"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_TITLE = "Tududi"
DEFAULT_ICON = "mdi:clipboard-text"

# Sensor constants
SENSOR_UPDATE_INTERVAL = 300  # 5 minutes
SENSOR_TIMEOUT = 30  # 30 seconds

# Addon detection - possible addon slugs
TUDUDI_ADDON_SLUGS = [
    "local_tududi_addon",
    "c2gl_tududi_addon",
    "tududi",
    "tududi_addon",
    "local_tududi",
]
