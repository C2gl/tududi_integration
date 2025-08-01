# Changelog

All notable changes to this project will be documented in this file.

## [0.3.0] - 2025-01-08

### Added
- **Todo Sensors**: New sensor platform that provides real-time todo information
  - `sensor.tududi_next_todo`: Shows the name of your next upcoming todo
  - `sensor.tududi_upcoming_todos_count`: Count of upcoming todos (excluding today's)
  - `sensor.tududi_today_todos_count`: Count of todos scheduled for today
- **Authentication Support**: Optional username/password configuration for API access
- **Rich Sensor Attributes**: Each sensor includes detailed task information:
  - Task ID, description, due date, priority, status
  - Project association, tags, creation/update timestamps
  - Smart prioritization (today's todos and high-priority tasks first)
- **Automatic Data Updates**: Sensors poll every 5 minutes for fresh todo data
- **Error Handling**: Robust authentication and API error handling

### Changed
- Updated configuration flow to include optional authentication fields
- Enhanced documentation with sensor usage examples and troubleshooting
- Bumped version to 0.3.0
- Added `aiohttp` as a requirement for API communication

### Technical Details
- New `sensor.py` platform with coordinator-based updates
- Session-based authentication with automatic re-authentication
- Intelligent task parsing and categorization
- Comprehensive error handling and logging

## [0.2.1] - Previous Release

### Features
- Tududi web panel integration
- Configurable panel titles and icons
- Multiple instance support
- Automatic panel cleanup on uninstall
