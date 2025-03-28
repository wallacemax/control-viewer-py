"""
Integration tests specific to the NiceGUI components of the Control Viewer application.
Tests the integration between NiceGUI and FastAPI.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock, AsyncMock
import json
import asyncio

# Add the parent directory to the path so we can import the needed modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try importing needed modules
try:
    from nicegui import ui
    from main import nicegui_app, fast_app
    NICEGUI_AVAILABLE = True
except ImportError:
    NICEGUI_AVAILABLE = False


@pytest.fixture
def nicegui_client():
    """
    Create a test client for the NiceGUI application.
    This is a bit tricky because NiceGUI doesn't have a test client like FastAPI.
    We'll mock the parts we need.
    """
    # Create a mock client
    client = MagicMock()
    
    # Add some methods for testing
    client.get = MagicMock()
    client.post = MagicMock()
    
    yield client


@pytest.mark.skipif(not NICEGUI_AVAILABLE, reason="NiceGUI module not available")
class TestNiceGUISetup:
    """
    Test the NiceGUI setup in the application.
    """
    
    def test_fastapi_mounted_to_nicegui(self):
        """
        Test that FastAPI app is mounted to NiceGUI correctly.
        """
        # Check that FastAPI app is mounted at /api
        assert '/api' in nicegui_app.routes
        
        # Check that it's the right app
        mounted_app = nicegui_app.routes['/api'].app
        assert mounted_app == fast_app
    
    def test_ui_pages_registered(self):
        """
        Test that UI pages are registered correctly.
        """
        # Check that main routes exist
        assert '/' in nicegui_app.routes
        assert '/about' in nicegui_app.routes
        assert '/test' in nicegui_app.routes
    
    def test_ui_page_functions_exist(self):
        """
        Test that UI page functions exist.
        """
        from main import index, about, test_page
        
        # Check that page functions exist and are callable
        assert callable(index)
        assert callable(about)
        assert callable(test_page)


@pytest.mark.skipif(not NICEGUI_AVAILABLE, reason="NiceGUI module not available")
class TestNiceGUIComponents:
    """
    Test the NiceGUI UI components used in the application.
    """
    
    @patch('nicegui.ui.card')
    @patch('nicegui.ui.label')
    def test_about_page_renders(self, mock_label, mock_card):
        """
        Test that the about page renders correctly.
        """
        # Configure mocks
        mock_card.return_value = MagicMock()
        mock_card.return_value.classes.return_value = mock_card.return_value
        mock_card.return_value.__enter__ = lambda x: mock_card.return_value
        mock_card.return_value.__exit__ = lambda x, y, z, a: None
        
        mock_label.return_value = MagicMock()
        mock_label.return_value.classes.return_value = mock_label.return_value
        
        # Call the about page function
        from main import about
        about()
        
        # Check that the card and labels were created
        assert mock_card.called
        assert mock_label.call_count >= 2  # At least app name and description
    
    @pytest.mark.asyncio
    @patch('nicegui.ui.card')
    @patch('nicegui.ui.label')
    @patch('ui.setup_layout')
    async def test_index_page_calls_setup_layout(self, mock_setup_layout, mock_label, mock_card):
        """
        Test that the index page calls setup_layout.
        """
        # Configure mocks
        mock_card.return_value = MagicMock()
        mock_card.return_value.classes.return_value = mock_card.return_value
        mock_card.return_value.__enter__ = lambda x: mock_card.return_value
        mock_card.return_value.__exit__ = lambda x, y, z, a: None
        
        mock_label.return_value = MagicMock()
        mock_label.return_value.classes.return_value = mock_label.return_value
        
        mock_setup_layout.return_value = None
        
        # Call the index page function
        from main import index
        index()
        
        # Check that setup_layout was called
        assert mock_setup_layout.called
    
    @pytest.mark.asyncio
    @patch('nicegui.ui.card')
    @patch('nicegui.ui.label')
    @patch('ui.setup_layout', side_effect=Exception("Test error"))
    async def test_index_page_handles_setup_error(self, mock_setup_layout, mock_label, mock_card):
        """
        Test that the index page handles errors in setup_layout.
        """
        # Configure mocks
        mock_card.return_value = MagicMock()
        mock_card.return_value.classes.return_value = mock_card.return_value
        mock_card.return_value.__enter__ = lambda x: mock_card.return_value
        mock_card.return_value.__exit__ = lambda x, y, z, a: None
        
        mock_label.return_value = MagicMock()
        mock_label.return_value.classes.return_value = mock_label.return_value
        
        # Call the index page function
        from main import index
        index()
        
        # Check that the error card was created
        assert mock_card.called
        card_classes = mock_card.return_value.classes.call_args[0][0]
        assert "bg-red-100" in card_classes
        
        # Check that error labels were created
        assert mock_label.called
        assert "Err loading application UI" in mock_label.call_args_list[0][0][0]


@pytest.mark.skipif(not NICEGUI_AVAILABLE, reason="NiceGUI module not available")
class TestNiceGUIIntegrationWithFastAPI:
    """
    Test the integration between NiceGUI and FastAPI.
    """
    
    def test_fastapi_endpoints_accessible_via_nicegui(self, test_client):
        """
        Test that FastAPI endpoints can be accessed via NiceGUI.
        """
        # Call the health endpoint which is provided by FastAPI
        response = test_client.get("/health")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    @patch('nicegui.ui.button')
    @patch('api.toggle_simulation')
    async def test_ui_buttons_call_api_functions(self, mock_toggle_simulation, mock_button):
        """
        Test that UI buttons call API functions.
        """
        # Configure mocks
        mock_button.return_value = MagicMock()
        mock_button.return_value.on.return_value = mock_button.return_value
        
        # Mock the API function to return a value
        mock_toggle_simulation.return_value = {"status": "started"}
        
        # Try to find and test a UI component that calls the API
        try:
            # This depends on the actual UI implementation
            from ui import create_simulation_toggle_button
            
            # Call the function that creates the button
            create_simulation_toggle_button()
            
            # Check that the button was created
            assert mock_button.called
            
            # Get the click handler
            click_handler = mock_button.return_value.on.call_args[0][1]
            
            # Call the click handler
            if asyncio.iscoroutinefunction(click_handler):
                await click_handler()
            else:
                click_handler()
            
            # Check that the API function was called
            assert mock_toggle_simulation.called
            
        except ImportError:
            pytest.skip("Function to create simulation toggle button not available")


@pytest.mark.skipif(True, reason="Browser tests require a running application")
class TestBrowserBasedNiceGUITests:
    """
    Browser-based tests for NiceGUI components.
    These tests require a running application and a browser.
    """
    
    def test_ui_renders_in_browser(self):
        """
        Test that the UI renders correctly in a browser.
        """
        # This would use Selenium or similar to check the UI
        # from selenium import webdriver
        # from selenium.webdriver.common.by import By
        # 
        # driver = webdriver.Chrome()
        # driver.get("http://localhost:8000")
        # 
        # # Check that main UI elements are present
        # assert "Control Viewer" in driver.title
        # assert driver.find_element(By.XPATH, "//div[contains(@class, 'q-tabs')]")
        # 
        # driver.quit()
        pass
    
    def test_ui_api_integration_in_browser(self):
        """
        Test UI-API integration in a browser.
        """
        # This would use Selenium or similar to test the integration
        # from selenium import webdriver
        # from selenium.webdriver.common.by import By
        # 
        # driver = webdriver.Chrome()
        # driver.get("http://localhost:8000")
        # 
        # # Find and click a button that calls the API
        # button = driver.find_element(By.ID, "toggle-simulation-button")
        # button.click()
        # 
        # # Check that the UI updates with the API response
        # import time
        # time.sleep(1)
        # status_element = driver.find_element(By.ID, "simulation-status")
        # assert "started" in status_element.text.lower()
        # 
        # driver.quit()
        pass