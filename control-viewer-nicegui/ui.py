"""
UI module for the Control Viewer application using NiceGUI
"""
from nicegui import ui, app
from datetime import datetime, timedelta
import asyncio
import json
from typing import Dict, List, Any, Callable, Optional
from models import ControlPoint, ControlGroup, SystemSettings, PointStatus

import httpx
import websockets

import time

from config import settings

API_BASE_URL = f'http://{settings.HOST}:{settings.PORT}/api'

# Singleton for storing page components that need to be accessed across functions
class UIState:
    def __init__(self):
        self.control_cards = None
        self.trend_chart = None
        self.connected_websocket = None
        self.points_by_id = {}
        self.selected_points_for_trend = set()
        self.trend_data = {}
        self.on_refresh_callback = None
                
        # Add these to store important container references
        self.selected_points_list = None
        self.chart_container = None
        self.settings_form = None
        self.table_container = None

        #debounce
        self.last_refresh_time = 0
        self.refresh_cooldown = 10

# Create singleton instance
ui_state = UIState()

# Helper functions
def format_timestamp(timestamp):
    """Format timestamp for display"""
    if not timestamp:
        return "Never"
    
    if isinstance(timestamp, str):
        try:
            # Parse the ISO format string into a datetime object
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            # Remove timezone info to make it naive
            timestamp = timestamp.replace(tzinfo=None)
        except ValueError:
            return timestamp
    
    # Make sure both datetimes are naive or both are aware
    now = datetime.now()
    
    # If timestamp has timezone but now doesn't, remove timezone
    if hasattr(timestamp, 'tzinfo') and timestamp.tzinfo is not None:
        timestamp = timestamp.replace(tzinfo=None)
    
    delta = now - timestamp
    
    if delta < timedelta(minutes=1):
        return "Just now"
    elif delta < timedelta(hours=1):
        minutes = int(delta.total_seconds() / 60)
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    elif delta < timedelta(days=1):
        hours = int(delta.total_seconds() / 3600)
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    else:
        return timestamp.strftime("%Y-%m-%d %H:%M")

def get_status_color(status: str) -> str:
    """Get color for status display"""
    colors = {
        "normal": "green",
        "warning": "orange",
        "alarm": "red",
        "error": "purple",
        "unknown": "gray"
    }
    return colors.get(status, "gray")

# Main dashboard page
def create_dashboard():
    """Create the dashboard page"""
    with ui.row().classes('w-full justify-between items-center'):
        ui.label('Control Dashboard').classes('text-h5')
        
        with ui.row():
            ui.button('Refresh', on_click=refresh_dashboard).props('icon=refresh')
            ui.button('Simulate', on_click=trigger_simulation).props('icon=science color=purple')
    
    # Create container for control cards
    ui_state.control_cards = ui.column().classes('w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4')

async def refresh_dashboard():
    """Refresh the dashboard with current data"""
    # Check refresh cooldown
    current_time = time.time()
    if current_time - ui_state.last_refresh_time < ui_state.refresh_cooldown:
        return
    
    ui_state.last_refresh_time = current_time
    
    try:
        # Fetch points from API
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{API_BASE_URL}/control-points')
        
        # Only process if we got a valid JSON response
        if response.text and ('application/json' in response.headers.get('content-type', '')):
            points = response.json()
            
            # Add type checking and error handling
            if not isinstance(points, list):
                if isinstance(points, dict) and 'data' in points:
                    points = points['data']
                else:
                    print(f"Unexpected API response format: {points}")
                    points = []  # Default to empty list to prevent errors
            
            # Create dictionary of new points by ID
            new_points_by_id = {point['id']: point for point in points}
            
            # Create a dictionary to keep track of card elements by point ID
            if not hasattr(ui_state, 'card_elements'):
                ui_state.card_elements = {}
            
            # Handle case where there are no points
            if not points and ui_state.control_cards:
                ui_state.control_cards.clear()
                with ui_state.control_cards:
                    ui.label('No control points available. Add some in the Configuration tab.')
                    ui.button('Add Sample Data', on_click=add_sample_data).props('color=primary')
                ui_state.card_elements = {}
                ui_state.points_by_id = {}
                return
            
            # Find points to remove (in current state but not in new data)
            points_to_remove = set(ui_state.points_by_id.keys()) - set(new_points_by_id.keys())
            for point_id in points_to_remove:
                if point_id in ui_state.card_elements:
                    ui_state.card_elements[point_id].delete()
                    del ui_state.card_elements[point_id]
            
            # Update or add points
            for point_id, point in new_points_by_id.items():
                old_point = ui_state.points_by_id.get(point_id)
                
                # Check if point is new or has changed
                is_new = point_id not in ui_state.points_by_id
                has_changed = not is_new and (
                    point.get('value') != old_point.get('value') or
                    point.get('status') != old_point.get('status') or
                    point.get('timestamp') != old_point.get('timestamp')
                )
                
                if is_new:
                    # Create new card for this point
                    if ui_state.control_cards:
                        with ui_state.control_cards:
                            ui_state.card_elements[point_id] = create_control_card(point)
                
                elif has_changed:
                    # Update existing card
                    if point_id in ui_state.card_elements:
                        # Remove old card
                        ui_state.card_elements[point_id].delete()
                        
                        # Create updated card
                        with ui_state.control_cards:
                            ui_state.card_elements[point_id] = create_control_card(point)
            
            # Update points_by_id with the latest data
            ui_state.points_by_id = new_points_by_id
            
        else:
            print("Response is not JSON or is empty")
            if ui_state.control_cards:
                ui_state.control_cards.clear()
                with ui_state.control_cards:
                    ui.label('API returned invalid or empty response').classes('text-negative')
                    ui.button('Retry', on_click=refresh_dashboard).props('color=primary')
        
        # Call the refresh callback if needed
        if ui_state.on_refresh_callback:
            await ui_state.on_refresh_callback()
            
    except Exception as e:
        print(f"Detailed error: {str(e)}")
        import traceback
        traceback.print_exc()
        ui.notify(f'Error refreshing dashboard: {str(e)}', type='negative')
        
        # Fallback UI when API call fails
        if ui_state.control_cards:
            ui_state.control_cards.clear()
            with ui_state.control_cards:
                ui.label('Error loading control points. API may not be available.').classes('text-negative')
                ui.button('Retry', on_click=refresh_dashboard).props('color=primary')

def create_control_card(point: Dict[str, Any]):
    point_id = point['id']
    point_type = point.get('type', 'scale')
    status = point.get('status')
    
    card = ui.card().classes('w-full')
    with card:
        with ui.row().classes('w-full items-center justify-between'):
            ui.label(point['name']).classes('text-h6')
            ui.icon('fiber_manual_record', color=get_status_color(status)).tooltip(f'Status: {status.capitalize()}')
        
        ui.separator()
            
        if point.get('description'):
            ui.label(point['description']).classes('text-caption')
        
        with ui.row().classes('w-full items-center justify-between'):
            value_text = f"{point.get('value', 'N/A')} {point.get('unit', '')}"
            
            if point_type == 'SCALE':
                ui.label(f"Value: {value_text}").classes('text-bold')
            else:  # actuator
                with ui.row().classes('items-center'):
                    value_input = ui.number(label='Value', value=point.get('value', 0))
                    
                    if point.get('min_value') is not None:
                        value_input.props(f"min={point['min_value']}")
                    
                    if point.get('max_value') is not None:
                        value_input.props(f"max={point['max_value']}")
                    
                    ui.button('Set', on_click=lambda v=value_input, pid=point_id: set_point_value(pid, v.value)).props('size=sm')
        
        if point.get('min_value') is not None and point.get('max_value') is not None:
            # Add a slider for range visualization
            current_value = point.get('value', 0)
            min_value = point.get('min_value', 0)
            max_value = point.get('max_value', 100)
            
            # Calculate percentage for progress bar
            if max_value > min_value:
                percentage = (current_value - min_value) / (max_value - min_value) * 100
                percentage = max(0, min(100, percentage))
            else:
                percentage = 50
            
            ui.linear_progress(value=percentage/100).classes('w-full')
            ui.label(f"Range: {min_value} - {max_value} {point.get('unit', '')}").classes('text-caption')
        
        ui.separator()
        
        with ui.row().classes('w-full items-center justify-between'):
            ui.label(f"Updated: {format_timestamp(point.get('timestamp'))}").classes('text-caption')
            
            with ui.row().classes('gap-2'):
                # Trend button to add/remove from trend view
                trend_button = ui.button(icon='show_chart', on_click=lambda pid=point_id: toggle_trend_point(pid))
                
                if point_id in ui_state.selected_points_for_trend:
                    trend_button.props('color=primary')
                
                # Edit button
                ui.button(icon='edit', on_click=lambda pid=point_id: edit_control_point(pid)).props('flat')
                
                # Delete button
                ui.button(icon='delete', on_click=lambda pid=point_id: delete_control_point(pid)).props('flat color=negative')

# Configuration page
def create_config_page():
    """Create the configuration page"""
    with ui.row().classes('w-full justify-between items-center'):
        ui.label('System Configuration').classes('text-h5')
        ui.button('Refresh', on_click=refresh_config).props('icon=refresh')
    
    with ui.tabs().classes('w-full') as tabs:
        points_tab = ui.tab('Control Points')
        groups_tab = ui.tab('Groups')
        settings_tab = ui.tab('Settings')
    
    with ui.tab_panels(tabs, value=points_tab).classes('w-full'):
        with ui.tab_panel(points_tab):
            create_control_points_config()
        
        with ui.tab_panel(groups_tab):
            create_groups_config()
        
        with ui.tab_panel(settings_tab):
            create_settings_config()

def create_control_points_config():
    """Create the control points configuration panel"""
    # Add New Control Point form
    with ui.card().classes('w-full'):
        ui.label('Add New Control Point').classes('text-h6')
        
        with ui.row().classes('w-full gap-4 flex-wrap'):
            point_id = ui.input('ID').props('required')
            point_name = ui.input('Name').props('required')
        
        point_desc = ui.input('Description')
        
        with ui.row().classes('w-full gap-4 flex-wrap'):
            point_type = ui.select(['scale', 'actuator'], label='Type').props('required')
            point_unit = ui.input('Unit')
        
        with ui.row().classes('w-full gap-4 flex-wrap'):
            point_min = ui.number('Min Value')
            point_max = ui.number('Max Value')
            point_value = ui.number('Initial Value')
        
        with ui.row().classes('w-full justify-end'):
            ui.button('Clear', on_click=lambda: clear_point_form(
    point_id, point_name, point_desc, point_type, point_unit, point_min, point_max, point_value
)).props('flat')
            ui.button('Add', on_click=lambda: add_control_point(
    point_id, point_name, point_desc, point_type, point_unit, point_min, point_max, point_value
)).props('color=primary')
    
    # List of existing points
    ui.label('Existing Control Points').classes('text-h6 mt-4')
    ui.button('Refresh List', on_click=refresh_config).props('icon=refresh')
    
    # Create table container
    table_container = ui.element('div').classes('w-full')
    
    # Define columns
    columns = [
        {'name': 'id', 'label': 'ID', 'field': 'id', 'sortable': True},
        {'name': 'name', 'label': 'Name', 'field': 'name', 'sortable': True},
        {'name': 'type', 'label': 'Type', 'field': 'type', 'sortable': True},
        {'name': 'value', 'label': 'Value', 'field': 'value', 'sortable': True},
        {'name': 'unit', 'label': 'Unit', 'field': 'unit'},
        {'name': 'actions', 'label': 'Actions', 'field': 'actions'}
    ]
    
    # Function to update the table data
    async def update_table_data():
        try:
            table_container.clear()

            async with httpx.AsyncClient() as client:
                response = await client.get(f'{API_BASE_URL}/control-points')
            points = response.json()
            
            # Create the table fresh each time
            with table_container:
                # Use the more modern ui.table approach
                with ui.table(columns=columns, rows=points, row_key='id').classes('w-full'):
                    # Add a template for the actions column
                    with ui.table_column('actions'):
                        def render_actions(item):
                            with ui.row().classes('gap-2'):
                                ui.button(icon='edit', on_click=lambda: edit_control_point(item['id'])).props('flat size=sm')
                                ui.button(icon='delete', on_click=lambda: delete_control_point(item['id'])).props('flat color=negative size=sm')
                        
                        # Register the template
                        ui.table_cell(render_actions)
                        
        except Exception as e:
            with table_container:
                ui.label(f"Error loading control points: {str(e)}").classes('text-negative')
    
    # Set the refresh callback
    ui_state.on_refresh_callback = update_table_data
    
    # Initial data load
    ui.timer(0.1, update_table_data, once=True)

def create_groups_config():
    """Create the groups configuration panel"""
    with ui.card().classes('w-full'):
        ui.label('Add New Group').classes('text-h6')
        
        with ui.row().classes('w-full gap-4 flex-wrap'):
            group_id = ui.input('ID').props('required')
            group_name = ui.input('Name').props('required')
        
        group_desc = ui.input('Description')
        
        ui.label('Select Control Points')
        points_select = ui.select(
            [], 
            label='Control Points', 
            multiple=True
        ).props('use-chips')
        
        # Update options when points are loaded
        async def update_point_options():
            async with httpx.AsyncClient() as client:
                response = await client.get(f'{API_BASE_URL}/control-points')
            points = response.json()
            options = [{'label': f"{p['name']} ({p['id']})", 'value': p['id']} for p in points]
            points_select.options = options
        
        # Set refresh callback
        ui_state.on_refresh_callback = update_point_options
        update_point_options()
        
        with ui.row().classes('w-full justify-end'):
            ui.button('Clear', on_click=lambda: [
                group_id.set_value(''),
                group_name.set_value(''),
                group_desc.set_value(''),
                points_select.set_value([])
            ]).props('flat')
            
            ui.button('Add', on_click=lambda: create_group(
                group_id.value,
                group_name.value,
                group_desc.value,
                points_select.value
            )).props('color=primary')

def create_settings_config():
    """Create the settings configuration panel"""
    with ui.card().classes('w-full'):
        ui.label('System Settings').classes('text-h6')
        
        settings_form = ui.element('div').classes('w-full')
        
        async def load_settings():
            async with httpx.AsyncClient() as client:
                response = await client.get(f'{API_BASE_URL}/settings')
            settings = response.json()
            
            settings_form.clear()
            
            with settings_form:
                refresh_rate = ui.slider(min=1, max=60, value=settings.get('refresh_rate', 5), step=1, label='Refresh Rate (seconds)')
                alarm_notification = ui.switch('Enable Alarm Notifications', value=settings.get('alarm_notification', True))
                data_retention = ui.number('Data Retention (days)', value=settings.get('data_retention_days', 30), min=1)
                theme = ui.select(['light', 'dark'], label='Theme', value=settings.get('theme', 'light'))
                
                ui.separator()
                
                with ui.row().classes('w-full justify-end'):
                    ui.button('Save Settings', on_click=lambda: save_settings(
                        refresh_rate.value,
                        alarm_notification.value,
                        data_retention.value,
                        theme.value
                    )).props('color=primary')
        
        load_settings()

# Trends page
def create_trends_page():

    # Function to refresh the trend chart
    async def refresh_trends():
        chart_container.clear()
        
        if not ui_state.selected_points_for_trend:
            with chart_container:
                ui.label('No points selected for trending').classes('text-center py-8')
            return
        
        # Determine time range
        now = datetime.now()
        start_time = None
        end_time = now
        
        if time_range.value == 'hour':
            start_time = now - timedelta(hours=1)
        elif time_range.value == 'day':
            start_time = now - timedelta(days=1)
        elif time_range.value == 'week':
            start_time = now - timedelta(weeks=1)
        elif time_range.value == 'month':
            start_time = now - timedelta(days=30)
        elif time_range.value == 'custom':
            try:
                start_time = datetime.fromisoformat(start_date.value + "T00:00:00")
                end_time = datetime.fromisoformat(end_date.value + "T23:59:59")
            except:
                ui.notify('Invalid date range', type='negative')
                start_time = now - timedelta(hours=1)
        
        # Fetch data for all selected points
        ui_state.trend_data = {}
        
        try:
            for point_id in ui_state.selected_points_for_trend:
                async with httpx.AsyncClient() as client:
                    response = await client.get(f'{API_BASE_URL}/historical-data/{point_id}',
                    params={
                        'start_time': start_time.isoformat() if start_time else None,
                        'end_time': end_time.isoformat()
                    }
                )
                
                data = response.json()
                if data.get('timestamps') and data.get('values'):
                    ui_state.trend_data[point_id] = {
                        'label': ui_state.points_by_id.get(point_id, {}).get('name', point_id),
                        'timestamps': data['timestamps'],
                        'values': data['values'],
                        'unit': ui_state.points_by_id.get(point_id, {}).get('unit', '')
                    }
            
            with chart_container:
                if not ui_state.trend_data:
                    ui.label('No historical data available for the selected time range').classes('text-center py-8')
                else:
                    create_trend_chart()
                    
        except Exception as e:
            ui.notify(f'Error fetching trend data: {str(e)}', type='negative')
            with chart_container:
                ui.label(f'Error loading trend data: {str(e)}').classes('text-negative text-center py-8')

    """Create the trends page"""
    with ui.row().classes('w-full justify-between items-center'):
        ui.label('Historical Trends').classes('text-h5')
        ui.button('Refresh', on_click=refresh_trends).props('icon=refresh')
    
    with ui.card().classes('w-full'):
        ui.label('Selected Control Points')
        selected_points_list = ui.element('div').classes('flex flex-wrap gap-2 my-2')
        
        # Time range selection
        with ui.row().classes('w-full items-end gap-4'):
            time_range_options = [
                    {'label': 'Last Hour', 'value': 'hour'},
                    {'label': 'Last Day', 'value': 'day'},
                    {'label': 'Last Week', 'value': 'week'},
                    {'label': 'Last Month', 'value': 'month'},
                    {'label': 'Custom Range', 'value': 'custom'}
                ]

            time_range = ui.select(
                options = time_range_options,
                label='Time Range'
            )

            time_range.value = 'hour'
            
            custom_range_container = ui.element('div').classes('flex gap-4')
            
            with custom_range_container:
                with ui.column():
                    ui.label('Start Date')
                    start_date = ui.date().props('disable')

                with ui.column():
                    ui.label('End Date')
                    end_date = ui.date().props('disable')
            
            # Show/hide custom range inputs based on selection
            def toggle_custom_range():
                if time_range.value == 'custom':
                    start_date.props.remove('disable')
                    end_date.props.remove('disable')
                else:
                    start_date.props('disable')
                    end_date.props('disable')
            
            time_range.on('update:model-value', toggle_custom_range)
            
            ui.button('Update Chart', on_click=refresh_trends).props('color=primary')
    
    # Chart container
    chart_container = ui.card().classes('w-full h-96')    
    
    # Function to update the selected points list
    async def update_selected_points_list():
        selected_points_list.clear()
        
        if not ui_state.selected_points_for_trend:
            with selected_points_list:
                ui.label('No points selected. Select points from the dashboard to view trends.')
        else:
            with selected_points_list:
                for point_id in ui_state.selected_points_for_trend:
                    point = ui_state.points_by_id.get(point_id, {"name": point_id})
                    with ui.chip(closable=True, on_close=lambda pid=point_id: remove_from_trend(pid)).classes('bg-primary text-white'):
                        ui.label(f"{point.get('name', 'Unknown')} ({point_id})")
    
    # Function to remove a point from trend view
    async def remove_from_trend(point_id):
        if point_id in ui_state.selected_points_for_trend:
            ui_state.selected_points_for_trend.remove(point_id)
            await update_selected_points_list()
            await refresh_trends()
    
    # Initialize
    update_selected_points_list()
    refresh_trends()

# Helper functions for the UI interactions
async def toggle_trend_point(point_id):
    """Toggle a point for trend view"""
    if point_id in ui_state.selected_points_for_trend:
        ui_state.selected_points_for_trend.remove(point_id)
    else:
        ui_state.selected_points_for_trend.add(point_id)
    
    # Refresh dashboard to update button states
    await refresh_dashboard()

async def set_point_value(point_id, new_value):
    """Set a new value for a control point"""
    try:
        if ui_state.connected_websocket:
            await ui_state.connected_websocket.send(json.dumps({
                "action": "update_value",
                "id": point_id,
                "value": new_value
            }))
            ui.notify(f"Value updated for {point_id}", type="positive")
        else:
            ui.notify("WebSocket not connected", type="negative")
    except Exception as e:
        ui.notify(f"Error updating value: {str(e)}", type="negative")

async def add_control_point(id_input, name_input, desc_input, type_input, unit_input, min_input, max_input, value_input):
    """Add a new control point"""
    try:
        new_point = {
            "id": id_input.value,
            "name": name_input.value,
            "description": desc_input.value,
            "type": type_input.value,
            "value": value_input.value,
            "unit": unit_input.value,
            "min_value": min_input.value,
            "max_value": max_input.value,
            "timestamp": datetime.now().isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{API_BASE_URL}/control-points', json=new_point)
        
        if response.status_code == 200:
            ui.notify(f"Created new control point: {new_point['name']}", type="positive")
            clear_point_form()
            await refresh_dashboard()
        else:
            ui.notify(f"Error: {response.text}", type="negative")
    except Exception as e:
        ui.notify(f"Error adding control point: {str(e)}", type="negative")

def clear_point_form(id_input, name_input, desc_input, type_input, unit_input, min_input, max_input, value_input):
        id_input.set_value("")
        name_input.set_value("")
        desc_input.set_value("")
        type_input.set_value("scale")
        unit_input.set_value("")
        min_input.set_value(None)
        max_input.set_value(None)
        value_input.set_value(None)

async def edit_control_point(point_id):
    """Edit an existing control point"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f'{API_BASE_URL}/control-points/{point_id}')
        point = response.json()
        
        # Create a dialog for editing
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f"Edit Control Point: {point['name']}").classes('text-h6')
            
            edit_name = ui.input('Name', value=point.get('name', ''))
            edit_desc = ui.input('Description', value=point.get('description', ''))
            edit_type = ui.select(['scale', 'actuator'], label='Type', value=point.get('type', 'scale'))
            edit_unit = ui.input('Unit', value=point.get('unit', ''))
            edit_min = ui.number('Min Value', value=point.get('min_value'))
            edit_max = ui.number('Max Value', value=point.get('max_value'))
            edit_value = ui.number('Current Value', value=point.get('value'))
            
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: save_edited_point(
                    point_id,
                    edit_name.value,
                    edit_desc.value,
                    edit_type.value,
                    edit_unit.value,
                    edit_min.value,
                    edit_max.value,
                    edit_value.value,
                    dialog
                )).props('color=primary')
        
        dialog.open()
    except Exception as e:
        ui.notify(f"Error editing point: {str(e)}", type="negative")

async def save_edited_point(point_id, name, desc, point_type, unit, min_val, max_val, value, dialog):
    """Save an edited control point"""
    try:
        point = {
            "id": point_id,
            "name": name,
            "description": desc,
            "type": point_type,
            "unit": unit,
            "min_value": min_val,
            "max_value": max_val,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(f'{API_BASE_URL}/control-points/{point_id}', json=point)
        
        if response.status_code == 200:
            dialog.close()
            ui.notify(f"Point updated: {name}", type="positive")
            await refresh_dashboard()
        else:
            ui.notify(f"Error: {response.text}", type="negative")
    except Exception as e:
        ui.notify(f"Error saving point: {str(e)}", type="negative")

async def delete_control_point(point_id):
    """Delete a control point"""
    def confirm_delete():
        # Use a non-async wrapper
        app.on_startup(lambda: asyncio.create_task(delete_point_confirmed(point_id)))
        return None
    
    ui.notify(f"Delete {point_id}?", type="warning", buttons=[
        {'label': 'Cancel', 'color': 'white'},
        {'label': 'Delete', 'color': 'negative', 'onClick': confirm_delete}
    ])

async def delete_point_confirmed(point_id):
    """Confirm and delete a control point"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f'{API_BASE_URL}/control-points/{point_id}')
        
        if response.status_code == 200:
            ui.notify(f"Point deleted: {point_id}", type="positive")
            
            # Remove from trend selection if present
            if point_id in ui_state.selected_points_for_trend:
                ui_state.selected_points_for_trend.remove(point_id)
            
            await refresh_dashboard()
        else:
            ui.notify(f"Error: {response.text}", type="negative")
    except Exception as e:
        ui.notify(f"Error deleting point: {str(e)}", type="negative")

async def create_group(group_id, name, description, points):
    """Create a new control group"""
    try:
        new_group = {
            "id": group_id,
            "name": name,
            "description": description,
            "points": points
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{API_BASE_URL}/control-groups', json=new_group)
        
        if response.status_code == 200:
            ui.notify(f"Created new group: {name}", type="positive")
            await refresh_config()
        else:
            ui.notify(f"Error: {response.text}", type="negative")
    except Exception as e:
        ui.notify(f"Error creating group: {str(e)}", type="negative")

async def save_settings(refresh_rate, alarm_notification, data_retention, theme):
    """Save system settings"""
    try:
        settings = {
            "refresh_rate": refresh_rate,
            "alarm_notification": alarm_notification,
            "data_retention_days": data_retention,
            "theme": theme
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.put(f'{API_BASE_URL}/settings', json=settings)
        
        if response.status_code == 200:
            ui.notify("Settings saved", type="positive")
        else:
            ui.notify(f"Error: {response.text}", type="negative")
    except Exception as e:
        ui.notify(f"Error saving settings: {str(e)}", type="negative")

async def refresh_config():
    """Refresh the configuration page"""
    await refresh_dashboard()

async def trigger_simulation():
    """Trigger a simulation of control point values"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f'{API_BASE_URL}/simulate')
        
        if response.status_code == 200:
            ui.notify("Simulation triggered", type="positive")
        else:
            ui.notify(f"Error: {response.text}", type="negative")
    except Exception as e:
        ui.notify(f"Error triggering simulation: {str(e)}", type="negative")

async def add_sample_data():
    """Add sample data for demonstration"""
    try:
        # Sample control points
        sample_points = [
            {
            "id": "{SOME_SCALE_NAME}-001",
            "name": "foo2024-09-27T23:27:50.817Z",
            "description": "This is what I call a target-rich environment.",
            "value": 42.7,
            "unit": "gram",
            "min_value": 0,
            "max_value": 100,
            "timestamp": "2024-09-27T23:27:50.817Z",
            "status": "normal",
            "type": "{SOME_SCALE_NAME}"
        },
        {
            "id": "{SOME_SCALE_NAME}-002",
            "name": "foo2024-09-29T19:20:34.453Z",
            "description": "Every time we go up there, it's unsafe.",
            "value": 55.4,
            "unit": "gram",
            "min_value": 0,
            "max_value": 100,
            "timestamp": "2024-09-29T19:20:34.453Z",
            "status": "normal",
            "type": "{SOME_SCALE_NAME}"
        },
        {
            "id": "{SOME_SCALE_NAME}-003",
            "name": "foo2024-10-01T15:13:18.089Z",
            "description": "That's right! Ice... man. I am dangerous.",
            "value": 39.5,
            "unit": "gram",
            "min_value": 0,
            "max_value": 100,
            "timestamp": "2024-10-01T15:13:18.089Z",
            "status": "normal",
            "type": "{SOME_SCALE_NAME}"
        }
        ]
        
        for point in sample_points:
            async with httpx.AsyncClient() as client:
                response = await client.post(f'{API_BASE_URL}/control-points', json=point)
        
        ui.notify("Sample data added", type="positive")
        await refresh_dashboard()
    except Exception as e:
        ui.notify(f"Error adding sample data: {str(e)}", type="negative")

def create_trend_chart():
    """Create a chart for trend data"""
    # Prepare data for the chart
    chart_data = []
    
    for point_id, data in ui_state.trend_data.items():
        if data['timestamps'] and data['values']:
            # Create dataset for each point
            dataset = {
                'label': f"{data['label']} ({data['unit']})",
                'data': [{'x': ts, 'y': val} for ts, val in zip(data['timestamps'], data['values'])],
                'borderColor': get_random_color(point_id),
                'tension': 0.1,
                'fill': False
            }
            chart_data.append(dataset)
    
    if not chart_data:
        ui.label('No data available for the selected time range').classes('text-center py-8')
        return
    
    # Create chart HTML
    chart_html = f"""
    <canvas id="trendChart" style="width: 100%; height: 100%;"></canvas>
    <script>
        const ctx = document.getElementById('trendChart').getContext('2d');
        const chart = new Chart(ctx, {{
            type: 'line',
            data: {{
                datasets: {json.dumps(chart_data)}
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        type: 'time',
                        time: {{
                            unit: 'minute',
                            displayFormats: {{
                                minute: 'HH:mm',
                                hour: 'HH:mm',
                                day: 'MMM D'
                            }}
                        }},
                        title: {{
                            display: true,
                            text: 'Time'
                        }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Value'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        position: 'top'
                    }},
                    tooltip: {{
                        mode: 'index',
                        intersect: false
                    }}
                }}
            }}
        }});
    </script>
    """
    
    ui.html(chart_html).classes('w-full h-full')

def get_random_color(seed):
    """Generate a deterministic color based on a seed string"""
    # Simple hash function to convert string to number
    hash_val = sum(ord(c) for c in seed)
    
    # Use predefined colors for better aesthetics
    colors = [
        'rgb(54, 162, 235)',   # blue
        'rgb(255, 99, 132)',   # red
        'rgb(75, 192, 192)',   # green
        'rgb(255, 159, 64)',   # orange
        'rgb(153, 102, 255)',  # purple
        'rgb(255, 205, 86)',   # yellow
        'rgb(201, 203, 207)',  # grey
        'rgb(255, 99, 71)',    # tomato
        'rgb(0, 128, 128)',    # teal
        'rgb(106, 90, 205)'    # slate blue
    ]
    
    return colors[hash_val % len(colors)]

# WebSocket connection
async def connect_websocket():
    """Establish WebSocket connection for real-time updates"""
    try:
        if not ui_state.connected_websocket:
            
            ws_url = f'ws://{settings.HOST}:{settings.PORT}/api/ws'
            
            ui_state.connected_websocket = await websockets.connect(ws_url)
            
            async def listener():
                while True:
                    try:
                        message = await ui_state.connected_websocket.recv()
                        data = json.loads(message)
                        
                        if data.get('action') in ['create', 'update', 'delete', 'simulate']:
                            # Use a JavaScript call to refresh the page instead
                            await ui.run_javascript('window.location.reload()')
                    except Exception as e:
                        print(f"WebSocket error: {str(e)}")
                        break
                
                # If we break out of the loop, try to reconnect
                ui_state.connected_websocket = None
                ui.timer(5.0, connect_websocket)
            
            asyncio.create_task(listener())
            ui.notify("Connected to real-time updates", type="positive")
        
    except Exception as e:
        print(f"WebSocket connection error (will retry): {str(e)}")
        ui_state.connected_websocket = None
        # Don't overwhelm with connection attempts if server is rejecting
        ui.timer(10.0, connect_websocket)  # Longer timeout

# Main app layout setup
def setup_layout():
    """Set up the main application layout"""
    # Add required CSS and JS
    ui.add_head_html('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">')
    ui.add_head_html('<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>')
    ui.add_head_html('<script src="https://cdn.jsdelivr.net/npm/moment@2.29.4/moment.min.js"></script>')
    ui.add_head_html('<script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-moment@1.0.1/dist/chartjs-adapter-moment.min.js"></script>')
    
    # Create header
    with ui.header().classes('bg-primary text-white'):
        ui.label('Control Viewer').classes('text-h4 q-ml-md')
    
    # Create tabs
    with ui.tabs().classes('w-full') as tabs:
        dashboard_tab = ui.tab('Dashboard')
        trends_tab = ui.tab('Trends')
        config_tab = ui.tab('Configuration')
    
    # Create tab panels
    with ui.tab_panels(tabs, value=dashboard_tab).classes('w-full'):
        with ui.tab_panel(dashboard_tab):
            create_dashboard()
        
        with ui.tab_panel(trends_tab):
            create_trends_page()
        
        with ui.tab_panel(config_tab):
            create_config_page()
    
    # Connect WebSocket and initialize dashboard
    ui.timer(0.1, connect_websocket)
    ui.timer(0.5, refresh_dashboard)