# Control Viewer

A modern web application for viewing and controlling industrial control systems. This project is built using NiceGUI for the frontend and FastAPI for the backend.

![Control Viewer Dashboard](https://raw.githubusercontent.com/YourUsername/control-viewer-nicegui/main/docs/images/dashboard_screenshot.png)

## Features

- Real-time monitoring of control points (sensors and actuators)
- Interactive dashboards with status indicators
- Trend visualization for historical data
- Control point configuration
- Grouping and organization of control points
- WebSocket-based real-time updates
- Responsive design for desktop and mobile

## Technology Stack

- **Backend**: FastAPI - a modern, fast web framework for building APIs with Python
- **Frontend**: NiceGUI - a Python library for building web UIs
- **Real-time Communication**: WebSockets
- **Data Visualization**: Chart.js
- **UI Components**: Bootstrap and NiceGUI components

## Project Structure

```
control-viewer-nicegui/
├── main.py              # Application entry point
├── config.py            # Configuration module
├── api.py               # API router and endpoints
├── database.py          # Data storage and persistence
├── models.py            # Data models
├── ui.py                # UI components and layout
├── utils.py             # Utility functions
├── requirements.txt     # Dependencies
├── data/                # Data directory for persistence
│   ├── control_points.json
│   ├── control_groups.json
│   └── settings.json
└── README.md            # This file
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/YourUsername/control-viewer-nicegui.git
cd control-viewer-nicegui
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py
```

4. Open your browser and navigate to `http://localhost:8080`

## Usage

### Dashboard

The dashboard provides a real-time view of all control points in the system. Each control point is displayed as a card showing its current value, status, and metadata. For actuators, you can directly set new values from the dashboard.

### Trends

The trends page allows you to visualize historical data for selected control points. You can:

- Select multiple points to compare their values
- Choose different time ranges (hour, day, week, month)
- Use custom date ranges for detailed analysis

### Configuration

The configuration page provides:

- Management of control points (add, edit, delete)
- Organization of points into logical groups
- System-wide settings like refresh rate and data retention policies

## API Documentation

When the application is running, API documentation is available at `http://localhost:8080/docs` or `http://localhost:8080/redoc`.

Key API endpoints:

- `/api/control-points` - CRUD operations for control points
- `/api/control-groups` - CRUD operations for control groups
- `/api/historical-data/{point_id}` - Historical data for a specific point
- `/api/settings` - System-wide settings
- `/api/ws` - WebSocket endpoint for real-time updates

## Development

### Running in Debug Mode

Set `DEBUG=True` in `config.py` to enable:

- Automatic reloading on code changes
- Detailed error messages
- Sample data simulation for testing

### Testing

The project includes comprehensive tests using pytest. To run the tests:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run only unit tests
python run_tests.py --unit

# Run only integration tests
python run_tests.py --integration

# Generate coverage report
python run_tests.py --coverage

# Run with verbose output
python run_tests.py --verbose
```

The test suite includes:

- Unit tests for all modules
- API endpoint tests
- Integration tests for end-to-end workflows

### Adding New Features

1. Implement backend logic in the appropriate module
2. Add API endpoints in `api.py`
3. Create UI components in `ui.py`
4. Update data models in `models.py` if needed
5. Add tests for new functionality

## Credits

This project is a port of the original [control-viewer](https://github.com/wallacemax/control-viewer) project, reimplemented using NiceGUI and FastAPI.

## License

MIT License