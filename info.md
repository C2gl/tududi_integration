# TuDuDi HACS Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A HACS integration to add [Tududi](https://github.com/chrisvel/tududi) as a sidebar panel in Home Assistant with todo sensors.

## Features

- **Web Panel**: Embed your Tududi server in a convenient sidebar panel
- **Todo Sensors**: Track your next upcoming todo, todo counts, and task details
- **Easy Configuration**: Setup through Home Assistant UI
- **Multiple Instances**: Support for multiple Tududi servers
- **Smart Prioritization**: Sensors prioritize today's todos and high-priority tasks

## Sensors

When authentication credentials are provided, the integration creates these sensors:

- **Next Todo**: Shows the name of your next upcoming todo
- **Upcoming Todos Count**: Number of upcoming todos (excluding today's)
- **Today Todos Count**: Number of todos scheduled for today

Each sensor includes rich attributes with task details like due dates, priority, project, tags, and more.

## Configuration

1. Install via HACS
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Tududi HACS"
5. Enter your Tududi server URL
6. Optionally provide username/password for todo sensors
7. Customize panel title and icon

## Requirements

- Home Assistant 2023.1.0+
- A running Tududi server instance
- HACS installed