"""
Integration tests for the Control Viewer application.
Tests the FastAPI endpoints and NiceGUI interface.
"""

import os
import sys
import pytest
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
import logging
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the main module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the FastAPI application and other needed components
from main import fast_app, nicegui_app
from config import settings
from database import database


# Configure test logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def test_client():
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(fast_app) as client:
        yield client


@pytest.fixture
async def async_client():
    """
    Create an async test client for the FastAPI application.
    """
    async with AsyncClient(app=fast_app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
def mock_database():
    """
    Mock the database to avoid actual database operations during testing.
    """
    with patch('database.database') as mock_db:
        # Configure mock database behavior here
        mock_db.is_connected = MagicMock(return_value=True)
        yield mock_db


@pytest.fixture(scope="module", autouse=True)
def mock_background_tasks():
    """
    Mock the background tasks to avoid starting actual background jobs during testing.
    """
    with patch('database.start_background_tasks') as mock_tasks:
        mock_tasks.return_value = asyncio.Future()
        mock_tasks.return_value.set_result(None)
        yield mock_tasks


@pytest.fixture(scope="module", autouse=True)
def mock_simulation():
    """
    Mock the simulation to avoid starting actual simulation during testing.
    """
    with patch('api.start_simulation') as mock_sim:
        yield mock_sim


@pytest.fixture(scope="module", autouse=True)
def create_data_dir():
    """
    Create data directory for tests if it doesn't exist.
    """
    os.makedirs("data", exist_ok=True)
    yield
    # We don't remove it after tests to avoid removing actual data


class TestFastAPIEndpoints:
    """
    Test FastAPI endpoints.
    """
    
    def test_health_check(self, test_client):
        """
        Test the health check endpoint.
        """
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == settings.APP_NAME
        assert data["version"] == settings.APP_VERSION
    
    async def test_health_check_async(self, async_client):
        """
        Test the health check endpoint using an async client.
        """
        response = await async_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestLifespanHandling:
    """
    Test application lifespan handling.
    """
    
    @pytest.mark.asyncio
    async def test_lifespan_startup(self, mock_background_tasks, mock_simulation):
        """
        Test that the lifespan context manager starts up correctly.
        """
        from main import lifespan
        
        # Create a mock app for the lifespan
        mock_app = MagicMock()
        
        # Execute the lifespan context manager
        async with lifespan(mock_app):
            # Check if background tasks were started
            assert mock_background_tasks.called
            
            # Check if simulation was started in debug mode
            if settings.DEBUG:
                assert mock_simulation.called
    
    @pytest.mark.skipif(not settings.DEBUG, reason="Only runs in debug mode")
    def test_simulation_started_in_debug(self, mock_simulation):
        """
        Test that simulation is started in debug mode.
        """
        # Import will trigger lifespan which should start simulation
        from main import fast_app
        assert mock_simulation.called


class TestNiceGUIIntegration:
    """
    Test NiceGUI integration.
    """
    
    @patch('ui.setup_layout')
    def test_index_page_renders(self, mock_setup_layout):
        """
        Test that the index page renders and calls setup_layout.
        """
        # We need to mock the ui.page decorator to capture the function call
        from main import index
        
        # Call the index function directly
        index()
        
        # Verify that setup_layout was called
        assert mock_setup_layout.called
    
    def test_about_page_content(self):
        """
        Test that the about page contains expected content.
        """
        # This is more difficult to test directly without rendering.
        # In a real test, we might use Selenium to check the rendered content.
        # For now, we'll check if the route exists
        
        # Check if the about route exists in nicegui_app
        from main import about
        assert callable(about)
    
    def test_api_mounted_to_nicegui(self):
        """
        Test that the FastAPI app is mounted to NiceGUI.
        """
        # Check if FastAPI is mounted to /api in nicegui_app
        assert '/api' in nicegui_app.routes
        
        # Additional check to ensure it's our FastAPI app
        mounted_app = nicegui_app.routes['/api'].app
        assert mounted_app == fast_app


class TestErrorHandling:
    """
    Test error handling in the application.
    """
    
    @patch('ui.setup_layout', side_effect=Exception("Test exception"))
    def test_index_error_handling(self, mock_setup_layout):
        """
        Test that errors in index page rendering are handled properly.
        """
        from main import index
        
        # We need to patch ui.card and ui.label to check they're used for error display
        with patch('nicegui.ui.card') as mock_card:
            mock_card.return_value = MagicMock()
            mock_card.return_value.classes.return_value = mock_card.return_value
            
            with patch('nicegui.ui.label') as mock_label:
                mock_label.return_value = MagicMock()
                mock_label.return_value.classes.return_value = mock_label.return_value
                
                # Call index, which should catch the exception
                index()
                
                # Verify error card was created
                assert mock_card.called
                assert "bg-red-100" in mock_card.return_value.classes.call_args[0][0]
                
                # Verify error labels were created
                assert mock_label.call_count >= 1
                assert "Err loading application UI" in mock_label.call_args_list[0][0][0]


if __name__ == "__main__":
    pytest.main(["-v"])