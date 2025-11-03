# Tududi HACS - Detailed Setup Guide

This guide provides detailed configuration examples and advanced usage scenarios for the Tududi HACS integration.

## Integration Modes

The Tududi integration can work in two different modes depending on your setup:

### Mode 1: Standalone External Server
Use this if you have Tududi running in an external Docker container or on another machine.

**What you get:**
- ✅ Sidebar iframe panel to access Tududi
- ✅ Todo sensors (if credentials provided)
- ✅ Full control over URL and configuration

**Configuration:**
- **Tududi Server URL**: Your external Tududi URL (e.g., `http://192.168.1.100:3000`)
- **Credentials**: Optional for sensor functionality

### Mode 2: With Tududi Add-on ⭐ RECOMMENDED
Use this if you have the [Tududi Add-on](https://github.com/c2gl/tududi_addon) installed in Home Assistant.

**What you get:**
- ✅ Integrated Home Assistant ingress (no iframe needed)
- ✅ Todo sensors connected to local add-on API
- ✅ Automatic detection - no duplicate panels
- ✅ Seamless experience

**How it works:**
1. Install the [Tududi Add-on](https://github.com/c2gl/tududi_addon)
2. Configure and start the add-on
3. Install this integration via HACS
4. Configure with add-on ingress URL and credentials
5. The integration automatically detects the add-on and only creates sensors!

**Configuration:**
- **Tududi Server URL**: Add-on ingress URL (check add-on documentation)
- **Credentials**: Your Tududi username/email and password (required for sensors)

**Important:** The add-on detection happens at integration startup. If you install the add-on after the integration:
1. Restart Home Assistant to trigger detection
2. The integration will detect the addon and will no longer create the iframe panel. If the panel was previously present, it will be removed after a restart or reload of the integration.
3. Sensors will continue to work normally

## Sensor Features

If you provide authentication credentials (username/email and password), the integration will create comprehensive sensors that track your todos:

### Available Sensors
- **Next Todo** (`sensor.tududi_next_todo`): Shows the name of your next upcoming todo
- **Upcoming Todos Count** (`sensor.tududi_upcoming_todos_count`): Number of upcoming todos (excluding today's todos)
- **Today Todos Count** (`sensor.tududi_today_todos_count`): Number of todos scheduled for today

### Sensor Intelligence
- **Smart Prioritization**: Today's todos take precedence over upcoming ones
- **Priority-Based Sorting**: Higher priority tasks are shown first
- **Automatic Filtering**: Completed tasks are automatically excluded
- **Fallback Logic**: If no scheduled todos exist, shows suggested tasks from Tududi metrics

### Rich Sensor Attributes
The **Next Todo** sensor includes detailed attributes:
- `task_id`: Unique identifier for the task
- `description`: Full task description/notes
- `due_date`: When the task is due (ISO format)
- `priority`: Priority level (0-3: Low, Medium, High, Critical)
- `priority_name`: Human-readable priority name
- `status`: Task status (0-4: Not Started, In Progress, Done, Waiting, Archived)
- `status_name`: Human-readable status name
- `project`: Associated project name (if any)
- `tags`: List of assigned tags
- `today`: Whether the task is marked for today
- `created_at` / `updated_at`: Timestamps

All sensors also include metrics data:
- `total_open_tasks`: Total number of open tasks
- `tasks_in_progress_count`: Number of tasks currently in progress
- `last_updated`: When the sensor data was last refreshed

## Sensor Usage Examples

### Lovelace Card Examples

#### Basic Next Todo Card
```yaml
type: entity
entity: sensor.tududi_next_todo
name: Next Todo
icon: mdi:clipboard-text
```

#### Advanced Todo Dashboard Card
```yaml
type: entities
title: Tududi Dashboard
entities:
  - entity: sensor.tududi_next_todo
    name: Next Todo
    secondary_info: |
      {% if state_attr('sensor.tududi_next_todo', 'due_date') %}
        Due: {{ (state_attr('sensor.tududi_next_todo', 'due_date') | as_datetime).strftime('%b %d') }}
      {% endif %}
      Priority: {{ state_attr('sensor.tududi_next_todo', 'priority_name') }}
  - entity: sensor.tududi_today_todos_count
    name: Today's Todos
    icon: mdi:calendar-today
  - entity: sensor.tududi_upcoming_todos_count
    name: Upcoming Todos
    icon: mdi:calendar-clock
```

#### Todo Summary Card with Attributes
```yaml
type: custom:auto-entities
card:
  type: entities
  title: Next Todo Details
filter:
  include:
    - entity_id: sensor.tududi_next_todo
      options:
        secondary_info: |
          {% set attrs = state_attr('sensor.tududi_next_todo', 'description') %}
          {% if attrs %}{{ attrs[:50] }}{% if attrs | length > 50 %}...{% endif %}{% endif %}
    - entity_id: sensor.tududi_next_todo
      name: "Due Date"
      state: |
        {% set due = state_attr('sensor.tududi_next_todo', 'due_date') %}
        {% if due %}{{ (due | as_datetime).strftime('%Y-%m-%d') }}{% else %}No due date{% endif %}
    - entity_id: sensor.tududi_next_todo
      name: "Priority"
      state: "{{ state_attr('sensor.tududi_next_todo', 'priority_name') }}"
    - entity_id: sensor.tududi_next_todo
      name: "Project"
      state: |
        {% set project = state_attr('sensor.tududi_next_todo', 'project') %}
        {{ project if project else 'No project' }}
```

### Automation Examples

#### Next Todo Notification
```yaml
automation:
  - alias: "Announce Next Todo"
    trigger:
      - platform: state
        entity_id: sensor.tududi_next_todo
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state != 'No upcoming todos' }}"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Next Todo"
          message: |
            {{ states('sensor.tududi_next_todo') }}
            {% set priority = state_attr('sensor.tududi_next_todo', 'priority_name') %}
            {% set due = state_attr('sensor.tududi_next_todo', 'due_date') %}
            Priority: {{ priority }}
            {% if due %}Due: {{ (due | as_datetime).strftime('%b %d, %Y') }}{% endif %}
```

#### High Priority Todo Alert
```yaml
automation:
  - alias: "High Priority Todo Alert"
    trigger:
      - platform: state
        entity_id: sensor.tududi_next_todo
    condition:
      - condition: template
        value_template: "{{ state_attr('sensor.tududi_next_todo', 'priority') | int >= 2 }}"
    action:
      - service: persistent_notification.create
        data:
          title: "🚨 High Priority Todo!"
          message: |
            {{ states('sensor.tududi_next_todo') }}
            Priority: {{ state_attr('sensor.tududi_next_todo', 'priority_name') }}
            {% set project = state_attr('sensor.tududi_next_todo', 'project') %}
            {% if project %}Project: {{ project }}{% endif %}
```

#### Daily Todo Summary
```yaml
automation:
  - alias: "Daily Todo Summary"
    trigger:
      - platform: time
        at: "08:00:00"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Daily Todo Summary"
          message: |
            Good morning! Here's your todo summary:
            📅 Today: {{ states('sensor.tududi_today_todos_count') }} todos
            📆 Upcoming: {{ states('sensor.tududi_upcoming_todos_count') }} todos
            ⭐ Next: {{ states('sensor.tududi_next_todo') }}
```

### Template Examples

#### Todo Summary Sensor
```yaml
template:
  - sensor:
      - name: "Todo Summary"
        state: >
          {% set next = states('sensor.tududi_next_todo') %}
          {% set today_count = states('sensor.tududi_today_todos_count') | int %}
          {% set upcoming_count = states('sensor.tududi_upcoming_todos_count') | int %}
          Today: {{ today_count }}, Upcoming: {{ upcoming_count }}
          {% if next != 'No upcoming todos' %}Next: {{ next }}{% endif %}
        attributes:
          today_count: "{{ states('sensor.tududi_today_todos_count') | int }}"
          upcoming_count: "{{ states('sensor.tududi_upcoming_todos_count') | int }}"
          next_todo: "{{ states('sensor.tududi_next_todo') }}"
          next_priority: "{{ state_attr('sensor.tududi_next_todo', 'priority_name') }}"
          next_due_date: "{{ state_attr('sensor.tududi_next_todo', 'due_date') }}"
```

#### Todo Progress Percentage
```yaml
template:
  - sensor:
      - name: "Todo Progress"
        state: >
          {% set total = state_attr('sensor.tududi_next_todo', 'total_open_tasks') | int %}
          {% set in_progress = state_attr('sensor.tududi_next_todo', 'tasks_in_progress_count') | int %}
          {% if total > 0 %}{{ ((in_progress / total) * 100) | round(1) }}{% else %}0{% endif %}
        unit_of_measurement: "%"
        attributes:
          total_tasks: "{{ state_attr('sensor.tududi_next_todo', 'total_open_tasks') }}"
          in_progress_tasks: "{{ state_attr('sensor.tududi_next_todo', 'tasks_in_progress_count') }}"
```

## Troubleshooting

### Sensors Not Working
- Ensure you provided valid username/email and password during configuration
- Check that your Tududi credentials allow API access
- Verify the Tududi server is accessible from Home Assistant
- Check Home Assistant logs for authentication errors
- The integration polls every 5 minutes - wait a few minutes after setup

### Common Issues
- **Authentication Failed**: Double-check your Tududi username/email and password
- **No Data**: Make sure your Tududi server has tasks and is accessible
- **Sensor Shows "Unknown"**: Wait a few minutes for the first data fetch, or check logs for errors

## Advanced Configuration

### Custom Refresh Interval
The sensors update every 5 minutes by default. This is configured in the integration code and currently cannot be changed through the UI.

### Multiple Tududi Servers
You can add multiple Tududi instances by repeating the configuration process with different URLs. Each instance will have its own set of sensors with unique entity IDs.
