"""
Integration tests for database operations in the Control Viewer application.
Tests the interaction between the application and the database layer.
"""

import pytest
import os
import sys
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import json
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import the needed modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import database module - handle import errors gracefully
try:
    import database
    from database import start_background_tasks
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False


@pytest.fixture
def sample_sensor_data():
    """
    Provides sample sensor data for tests.
    """
    return {
        "id": "test-sensor-001",
        "name": "Test Temperature Sensor",
        "description": "A sensor for testing",
        "value": 24.5,
        "unit": "°C",
        "min_value": 0.0,
        "max_value": 100.0,
        "timestamp": datetime.now().isoformat(),
        "status": "normal",
        "type": "sensor"
    }


@pytest.fixture
def sample_sensor_history():
    """
    Provides sample sensor history data for tests.
    """
    now = datetime.now()
    history = []
    
    # Generate 10 history points with decreasing timestamps
    for i in range(10):
        timestamp = now - timedelta(minutes=i*15)
        history.append({
            "timestamp": timestamp.isoformat(),
            "value": 24.0 + (i * 0.5)
        })
    
    return history


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database module not available")
class TestDatabaseOperations:
    """
    Test the database operations used by the application.
    """
    
    @pytest.mark.asyncio
    @patch('database.database')
    async def test_start_background_tasks(self, mock_db):
        """
        Test that background tasks are started correctly.
        """
        # Configure the mock
        mock_db.start_sensor_polling = AsyncMock()
        mock_db.start_data_cleanup = AsyncMock()
        
        # Call the function
        await start_background_tasks()
        
        # Check that the background tasks were started
        assert mock_db.start_sensor_polling.called
        assert mock_db.start_data_cleanup.called
    
    @patch('database.database')
    def test_get_all_sensors(self, mock_db):
        """
        Test retrieving all sensors from the database.
        """
        # Configure the mock
        mock_sensors = [
            {"id": "sensor-001", "name": "Sensor 1"},
            {"id": "sensor-002", "name": "Sensor 2"}
        ]
        mock_db.get_sensors = MagicMock(return_value=mock_sensors)
        
        # Call the function
        result = database.get_all_sensors()
        
        # Check the result
        assert result == mock_sensors
        assert mock_db.get_sensors.called
    
    @patch('database.database')
    def test_get_sensor_by_id(self, mock_db, sample_sensor_data):
        """
        Test retrieving a sensor by ID from the database.
        """
        # Configure the mock
        sensor_id = "test-sensor-001"
        mock_db.get_sensor = MagicMock(return_value=sample_sensor_data)
        
        # Call the function
        result = database.get_sensor_by_id(sensor_id)
        
        # Check the result
        assert result == sample_sensor_data
        mock_db.get_sensor.assert_called_with(sensor_id)
    
    @patch('database.database')
    def test_get_sensor_by_id_not_found(self, mock_db):
        """
        Test retrieving a non-existent sensor by ID.
        """
        # Configure the mock
        sensor_id = "non-existent-sensor"
        mock_db.get_sensor = MagicMock(return_value=None)
        
        # Call the function
        result = database.get_sensor_by_id(sensor_id)
        
        # Check the result
        assert result is None
        mock_db.get_sensor.assert_called_with(sensor_id)
    
    @patch('database.database')
    def test_get_sensor_history(self, mock_db, sample_sensor_history):
        """
        Test retrieving sensor history from the database.
        """
        # Configure the mock
        sensor_id = "test-sensor-001"
        mock_db.get_history = MagicMock(return_value=sample_sensor_history)
        
        # Call the function
        result = database.get_sensor_history(sensor_id)
        
        # Check the result
        assert result == sample_sensor_history
        mock_db.get_history.assert_called_with(sensor_id)
    
    @patch('database.database')
    def test_update_sensor(self, mock_db, sample_sensor_data):
        """
        Test updating a sensor in the database.
        """
        # Configure the mock
        sensor_id = "test-sensor-001"
        updated_data = {"value": 26.8}
        expected_result = {**sample_sensor_data, **updated_data}
        mock_db.update_sensor_data = MagicMock(return_value=expected_result)
        
        # Call the function
        result = database.update_sensor(sensor_id, updated_data)
        
        # Check the result
        assert result == expected_result
        mock_db.update_sensor_data.assert_called_with(sensor_id, updated_data)


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database module not available")
class TestDatabaseFileOperations:
    """
    Test the file-based database operations.
    """
    
    @pytest.fixture
    def mock_data_file(self):
        """
        Create a temporary data file for testing.
        """
        # Create a temporary directory for test data
        os.makedirs("test_data", exist_ok=True)
        
        # Create a mock data file
        file_path = os.path.join("test_data", "sensors.json")
        test_data = [
            {
                "id": "sensor-001",
                "name": "Test Sensor 1",
                "value": 25.0,
                "status": "normal"
            },
            {
                "id": "sensor-002",
                "name": "Test Sensor 2",
                "value": 1013.25,
                "status": "warning"
            }
        ]
        
        with open(file_path, 'w') as f:
            json.dump(test_data, f)
            
        yield file_path
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove the test directory if empty
        try:
            os.rmdir("test_data")
        except OSError:
            pass
    
    @patch('database.DATA_DIR', 'test_data')
    @patch('database.SENSORS_FILE', 'sensors.json')
    def test_load_data_from_file(self, mock_data_file):
        """
        Test loading data from a file.
        """
        # Assuming there's a load_data function in the database module
        if hasattr(database, 'load_data'):
            # Call the function
            data = database.load_data()
            
            # Check the result
            assert len(data) == 2
            assert data[0]["id"] == "sensor-001"
            assert data[1]["id"] == "sensor-002"
        else:
            pytest.skip("load_data function not available in database module")
    
    @patch('database.DATA_DIR', 'test_data')
    @patch('database.SENSORS_FILE', 'new_sensors.json')
    def test_save_data_to_file(self):
        """
        Test saving data to a file.
        """
        # Prepare test data
        test_data = [
            {
                "id": "sensor-001",
                "name": "New Sensor 1",
                "value": 26.5,
                "status": "normal"
            }
        ]
        
        # Assuming there's a save_data function in the database module
        if hasattr(database, 'save_data'):
            # Call the function
            database.save_data(test_data)
            
            # Check that the file was created
            file_path = os.path.join("test_data", "new_sensors.json")
            assert os.path.exists(file_path)
            
            # Check the file contents
            with open(file_path, 'r') as f:
                saved_data = json.load(f)
                assert len(saved_data) == 1
                assert saved_data[0]["id"] == "sensor-001"
                assert saved_data[0]["value"] == 26.5
            
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
        else:
            pytest.skip("save_data function not available in database module")


@pytest.mark.skipif(not DATABASE_AVAILABLE, reason="Database module not available")
class TestBackgroundTasks:
    """
    Test the background tasks that interact with the database.
    """
    
    @pytest.mark.asyncio
    @patch('database.database.update_sensors')
    @patch('asyncio.sleep', return_value=None)
    async def test_sensor_polling(self, mock_sleep, mock_update_sensors):
        """
        Test the sensor polling background task.
        """
        # Configure the mock
        mock_update_sensors.return_value = None
        
        # Create a polling coroutine
        if hasattr(database, 'sensor_polling_task'):
            # Create a flag to stop the task
            running = True
            
            # Define a wrapper to run the task for a short time
            async def run_polling_task():
                nonlocal running
                poll_task = database.sensor_polling_task()
                try:
                    # Run the task for a short time
                    for _ in range(3):
                        if asyncio.iscoroutine(poll_task):
                            await asyncio.wait_for(poll_task, timeout=0.1)
                        if not running:
                            break
                        await asyncio.sleep(0.1)
                except asyncio.TimeoutError:
                    # Expected if the task is an infinite loop
                    pass
                finally:
                    running = False
            
            # Run the task
            await run_polling_task()
            
            # Check that update_sensors was called
            assert mock_update_sensors.called
        else:
            pytest.skip("sensor_polling_task function not available in database module")
    
    @pytest.mark.asyncio
    @patch('database.database.cleanup_old_data')
    @patch('asyncio.sleep', return_value=None)
    async def test_data_cleanup(self, mock_sleep, mock_cleanup):
        """
        Test the data cleanup background task.
        """
        # Configure the mock
        mock_cleanup.return_value = None
        
        # Create a cleanup coroutine
        if hasattr(database, 'data_cleanup_task'):
            # Create a flag to stop the task
            running = True
            
            # Define a wrapper to run the task for a short time
            async def run_cleanup_task():
                nonlocal running
                cleanup_task = database.data_cleanup_task()
                try:
                    # Run the task for a short time
                    for _ in range(3):
                        if asyncio.iscoroutine(cleanup_task):
                            await asyncio.wait_for(cleanup_task, timeout=0.1)
                        if not running:
                            break
                        await asyncio.sleep(0.1)
                except asyncio.TimeoutError:
                    # Expected if the task is an infinite loop
                    pass
                finally:
                    running = False
            
            # Run the task
            await run_cleanup_task()
            
            # Check that cleanup_old_data was called
            assert mock_cleanup.called
        else:
            pytest.skip("data_cleanup_task function not available in database module")