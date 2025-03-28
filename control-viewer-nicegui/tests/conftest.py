"""
Pytest configuration file for Control Viewer tests.
Contains shared fixtures and configuration for all tests.
"""

import os
import sys
import asyncio
import pytest
from unittest.mock import patch, MagicMock

# Make sure the application root directory is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure(config):
    """
    Configure pytest environment before tests run.
    """
    # Set environment variables for testing
    os.environ["APP_ENV"] = "testing"
    # You might want to set other environment variables here


@pytest.fixture(scope="session")
def event_loop():
    """
    Create and provide an event loop for async tests.
    This allows reusing the same event loop for the entire test session.
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    yield loop
    
    # Close the event loop at the end of the session
    loop.close()


@pytest.fixture(autouse=True)
def mock_ui_components():
    """
    Mock NiceGUI UI components to prevent them from rendering during tests.
    This is needed because NiceGUI relies on the web client which isn't available during tests.
    """
    # Create a class to mock UI elements
    class MockUIElement:
        def __init__(self, *args, **kwargs):
            pass
        
        def __call__(self, *args, **kwargs):
            return self
        
        def classes(self, *args, **kwargs):
            return self
        
        def style(self, *args, **kwargs):
            return self
        
        def on(self, *args, **kwargs):
            return lambda *args, **kwargs: None
    
    # List of UI components to mock
    ui_components = [
        'nicegui.ui.page',
        'nicegui.ui.card',
        'nicegui.ui.label',
        'nicegui.ui.button',
        'nicegui.ui.row',
        'nicegui.ui.column',
        'nicegui.ui.tabs',
        'nicegui.ui.tab',
        'nicegui.ui.tab_panel',
        'nicegui.ui.tab_panels',
        'nicegui.ui.dialog',
    ]
    
    # Create patches for each UI component
    patches = []
    for component in ui_components:
        # Create a decorator mock for ui.page
        if component == 'nicegui.ui.page':
            page_mock = MagicMock()
            page_mock.return_value = lambda func: func
            p = patch(component, page_mock)
        else:
            p = patch(component, return_value=MockUIElement())
        
        patches.append(p)
    
    # Apply all patches
    for p in patches:
        p.start()
    
    yield
    
    # Remove all patches
    for p in patches:
        p.stop()