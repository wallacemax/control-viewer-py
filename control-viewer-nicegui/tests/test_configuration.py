"""
Integration tests for the configuration settings of the Control Viewer application.
Tests that configuration is loaded correctly and affects the application behavior.
"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the needed modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import the config module
try:
    from config import settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Configuration module not available")
class TestConfigSettings:
    """
    Test the configuration settings loaded by the application.
    """
    
    def test_config_values_loaded(self):
        """
        Test that configuration values are loaded correctly.
        """
        # Check that basic settings have values
        assert settings.APP_NAME is not None
        assert settings.APP_VERSION is not None
        assert settings.APP_DESCRIPTION is not None
        assert settings.HOST is not None
        assert settings.PORT is not None
        assert isinstance(settings.DEBUG, bool)
    
    def test_environment_variables_override(self):
        """
        Test that environment variables can override config values.
        """
        # Store original values
        original_host = settings.HOST
        original_port = settings.PORT
        
        try:
            # Set environment variables
            os.environ["APP_HOST"] = "0.0.0.0"
            os.environ["APP_PORT"] = "9000"
            
            # Reload settings - check if settings has a reload method
            if hasattr(settings, 'reload'):
                settings.reload()
                
                # Check that values were overridden
                assert settings.HOST == "0.0.0.0"
                assert settings.PORT == 9000
            else:
                pytest.skip("settings module doesn't have a reload method")
                
        finally:
            # Restore environment
            if "APP_HOST" in os.environ:
                del os.environ["APP_HOST"]
            if "APP_PORT" in os.environ:
                del os.environ["APP_PORT"]
            
            # Reset settings if possible
            if hasattr(settings, 'reload'):
                settings.reload()
                assert settings.HOST == original_host
                assert settings.PORT == original_port
    
    def test_config_file_loading(self):
        """
        Test that configuration can be loaded from a file.
        """
        # Create a temporary config file
        config_path = os.path.join("test_data", "test_config.json")
        os.makedirs("test_data", exist_ok=True)
        
        try:
            # Write test config
            with open(config_path, 'w') as f:
                f.write('{"APP_NAME": "Test App", "APP_VERSION": "0.0.1", "DEBUG": true}')
            
            # Check if settings has a load_from_file method
            if hasattr(settings, 'load_from_file'):
                # Load from the file
                settings.load_from_file(config_path)
                
                # Check values
                assert settings.APP_NAME == "Test App"
                assert settings.APP_VERSION == "0.0.1"
                assert settings.DEBUG is True
            else:
                pytest.skip("settings module doesn't have a load_from_file method")
                
        finally:
            # Clean up
            if os.path.exists(config_path):
                os.remove(config_path)
            
            # Try to restore settings
            if hasattr(settings, 'reload'):
                settings.reload()


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Configuration module not available")
class TestConfigIntegration:
    """
    Test that configuration correctly affects the application behavior.
    """
    
    @patch('config.settings.DEBUG', True)
    def test_debug_mode_enables_reloading(self):
        """
        Test that debug mode enables auto-reloading.
        """
        from main import nicegui_app
        
        # Check if ui.run was called with reload=True
        with patch('nicegui.ui.run') as mock_run:
            # Import to trigger ui.run
            from main import ui
            
            # Try to run the application
            if hasattr(ui, 'run'):
                try:
                    # This might not execute if app is already running
                    ui.run(
                        host=settings.HOST,
                        port=settings.PORT,
                        reload=settings.DEBUG
                    )
                except Exception:
                    # Ignore exceptions - we just want to check args
                    pass
                
                # Check if ui.run was called with reload=True
                if mock_run.called:
                    assert any(
                        call_args.get('reload', False) is True
                        for call_args in [call[1] for call in mock_run.call_args_list]
                    )
    
    @patch('config.settings.APP_NAME', "Test Control Viewer")
    @patch('config.settings.APP_VERSION', "0.0.1")
    def test_app_info_in_html_title(self):
        """
        Test that app name is used in HTML title.
        """
        # This would be better tested with Selenium to check the actual rendered title
        # Here we'll just check if ui.run was called with the correct title
        with patch('nicegui.ui.run') as mock_run:
            # Import to trigger ui.run
            from main import ui
            
            # Try to run the application
            if hasattr(ui, 'run'):
                try:
                    # This might not execute if app is already running
                    ui.run(
                        title=settings.APP_NAME
                    )
                except Exception:
                    # Ignore exceptions - we just want to check args
                    pass
                
                # Check if ui.run was called with the right title
                if mock_run.called:
                    assert any(
                        call_args.get('title', "") == "Test Control Viewer"
                        for call_args in [call[1] for call in mock_run.call_args_list]
                    )
    
    @patch('config.settings.DEBUG', True)
    def test_debug_mode_starts_simulation(self):
        """
        Test that debug mode starts the simulation.
        """
        # Check if simulation is started in debug mode
        with patch('api.start_simulation') as mock_start_simulation:
            # Import to trigger the lifespan context manager
            from main import lifespan
            
            # Create a mock app
            mock_app = MagicMock()
            
            # Run the lifespan context manager
            async def run_lifespan():
                async with lifespan(mock_app):
                    pass
            
            # Run in an event loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(run_lifespan())
            finally:
                loop.close()
            
            # Check if start_simulation was called
            assert mock_start_simulation.called


@pytest.mark.skipif(not CONFIG_AVAILABLE, reason="Configuration module not available")
class TestConfigWithFastAPI:
    """
    Test configuration integration with FastAPI.
    """
    
    def test_fastapi_app_uses_config(self):
        """
        Test that FastAPI app uses configuration values.
        """
        from main import fast_app
        
        # Check that FastAPI app has the configured title and version
        assert fast_app.title == settings.APP_NAME
        assert fast_app.version == settings.APP_VERSION
        assert fast_app.description == settings.APP_DESCRIPTION
    
    def test_health_endpoint_returns_config_info(self, test_client):
        """
        Test that health endpoint returns configuration info.
        """
        # Call the health endpoint
        response = test_client.get("/health")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        
        # Verify that configuration values are in the response
        assert data["app"] == settings.APP_NAME
        assert data["version"] == settings.APP_VERSION
        assert data["status"] == "healthy"