"""
Integration tests for the simulation functionality in the Control Viewer application.
Tests the simulation components that generate test data.
"""

import pytest
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import time

# Add the parent directory to the path so we can import the needed modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import simulation-related modules
try:
    from api import start_simulation, stop_simulation, toggle_simulation
    SIMULATION_AVAILABLE = True
except ImportError:
    SIMULATION_AVAILABLE = False


@pytest.fixture
def mock_simulation_task():
    """
    Mock the simulation task
    """
    with patch('api.simulation_task') as mock_task:
        mock_task.return_value = AsyncMock()
        yield mock_task


@pytest.fixture
def mock_database():
    """
    Mock the database module
    """
    with patch('api.database') as mock_db:
        mock_db.update_sensor = MagicMock()
        mock_db.get_all_sensors = MagicMock(return_value=[
            {"id": "sensor-001", "name": "Test Sensor 1", "value": 25.0, "status": "normal"},
            {"id": "sensor-002", "name": "Test Sensor 2", "value": 50.0, "status": "normal"}
        ])
        yield mock_db


@pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
class TestSimulationControl:
    """
    Test the simulation control functions.
    """
    
    def test_start_simulation(self, mock_simulation_task):
        """
        Test starting the simulation.
        """
        # Call the function
        result = start_simulation()
        
        # Check the result
        assert result["status"] == "started"
        assert mock_simulation_task.called
    
    @patch('api.SIMULATION_RUNNING', True)
    def test_stop_simulation(self):
        """
        Test stopping the simulation.
        """
        # Call the function
        result = stop_simulation()
        
        # Check the result
        assert result["status"] == "stopped"
        
        # Check that the simulation flag was changed
        from api import SIMULATION_RUNNING
        assert not SIMULATION_RUNNING
    
    @patch('api.SIMULATION_RUNNING', False)
    def test_toggle_simulation_start(self, mock_simulation_task):
        """
        Test toggling the simulation from stopped to started.
        """
        # Call the function
        result = toggle_simulation()
        
        # Check the result
        assert result["status"] == "started"
        assert mock_simulation_task.called
    
    @patch('api.SIMULATION_RUNNING', True)
    def test_toggle_simulation_stop(self):
        """
        Test toggling the simulation from started to stopped.
        """
        # Call the function
        result = toggle_simulation()
        
        # Check the result
        assert result["status"] == "stopped"
        
        # Check that the simulation flag was changed
        from api import SIMULATION_RUNNING
        assert not SIMULATION_RUNNING


@pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
class TestSimulationTask:
    """
    Test the simulation task that generates data.
    """
    
    @pytest.mark.asyncio
    async def test_simulation_task_updates_sensors(self, mock_database):
        """
        Test that the simulation task updates sensor values.
        """
        # Import the simulation task directly
        try:
            from api import simulation_task
            
            # Set up the simulation to run briefly
            from api import SIMULATION_RUNNING
            
            # Create a wrapper to run the task for a short time
            async def run_simulation():
                # Set the simulation to running
                api.SIMULATION_RUNNING = True
                
                # Run the task in the background
                task = asyncio.create_task(simulation_task())
                
                # Let it run briefly
                await asyncio.sleep(0.2)
                
                # Stop the simulation
                api.SIMULATION_RUNNING = False
                
                # Wait for the task to complete
                try:
                    await asyncio.wait_for(task, timeout=0.5)
                except asyncio.TimeoutError:
                    # Cancel the task if it doesn't complete in time
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Run the simulation
            await run_simulation()
            
            # Check that the database update function was called
            assert mock_database.update_sensor.called
            
        except ImportError:
            pytest.skip("simulation_task function not available in api module")
    
    @pytest.mark.skipif(True, reason="Long-running test")
    @pytest.mark.asyncio
    async def test_simulation_task_long_running(self, mock_database):
        """
        Test the simulation task over a longer period to ensure it continues to update values.
        This test is skipped by default as it's long-running.
        """
        # Import the simulation task directly
        try:
            from api import simulation_task
            
            # Set up the simulation to run for a longer time
            from api import SIMULATION_RUNNING
            
            # Create a wrapper to run the task for a longer time
            async def run_simulation_longer():
                # Set the simulation to running
                api.SIMULATION_RUNNING = True
                
                # Run the task in the background
                task = asyncio.create_task(simulation_task())
                
                # Let it run for a few seconds
                await asyncio.sleep(5)
                
                # Stop the simulation
                api.SIMULATION_RUNNING = False
                
                # Wait for the task to complete
                try:
                    await asyncio.wait_for(task, timeout=1)
                except asyncio.TimeoutError:
                    # Cancel the task if it doesn't complete in time
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            # Run the simulation
            await run_simulation_longer()
            
            # Check that the database update function was called multiple times
            assert mock_database.update_sensor.call_count > 3
            
        except ImportError:
            pytest.skip("simulation_task function not available in api module")


@pytest.mark.skipif(not SIMULATION_AVAILABLE, reason="Simulation module not available")
class TestSimulationDataGeneration:
    """
    Test the data generation functions used by the simulation.
    """
    
    def test_generate_random_sensor_value(self):
        """
        Test generating random sensor values.
        """
        # Try to import the function
        try:
            from api import generate_random_sensor_value
            
            # Call the function with a base value and range
            base_value = 50.0
            value_range = 10.0
            
            # Generate several values
            values = [generate_random_sensor_value(base_value, value_range) for _ in range(10)]
            
            # Check that all values are within the expected range
            for value in values:
                assert base_value - value_range <= value <= base_value + value_range
            
            # Check that we got different values (very unlikely to get all the same)
            assert len(set(values)) > 1
            
        except ImportError:
            pytest.skip("generate_random_sensor_value function not available in api module")
    
    def test_generate_sensor_status(self):
        """
        Test generating sensor status based on value.
        """
        # Try to import the function
        try:
            from api import generate_sensor_status
            
            # Call the function with different values
            normal_value = 50.0
            warning_value_low = 20.0
            warning_value_high = 80.0
            critical_value_low = 5.0
            critical_value_high = 95.0
            
            # Use default min/max for the tests
            min_value = 0.0
            max_value = 100.0
            
            # Check the statuses
            assert generate_sensor_status(normal_value, min_value, max_value) == "normal"
            assert generate_sensor_status(warning_value_low, min_value, max_value) == "warning"
            assert generate_sensor_status(warning_value_high, min_value, max_value) == "warning"
            assert generate_sensor_status(critical_value_low, min_value, max_value) == "critical"
            assert generate_sensor_status(critical_value_high, min_value, max_value) == "critical"
            
        except ImportError:
            pytest.skip("generate_sensor_status function not available in api module")


@pytest.mark.skipif(True, reason="System test requiring full application")
class TestSimulationSystemTests:
    """
    System tests for the simulation functionality.
    These tests require the full application to be running.
    Skipped by default as they are system tests.
    """
    
    def test_simulation_affects_ui(self):
        """
        Test that the simulation affects the UI.
        This would use Selenium or similar to check the UI updates.
        """
        # Example using Selenium (not implemented)
        # from selenium import webdriver
        # from selenium.webdriver.common.by import By
        # driver = webdriver.Chrome()
        # driver.get("http://localhost:8000")
        # 
        # # Find and click the simulation toggle button
        # toggle_button = driver.find_element(By.ID, "simulation-toggle")
        # toggle_button.click()
        # 
        # # Wait for UI to update
        # time.sleep(2)
        # 
        # # Check that sensor values are changing
        # sensor_value_1 = driver.find_element(By.ID, "sensor-001-value").text
        # time.sleep(2)
        # sensor_value_2 = driver.find_element(By.ID, "sensor-001-value").text
        # 
        # # Values should be different after simulation runs
        # assert sensor_value_1 != sensor_value_2
        # 
        # driver.quit()
        pass