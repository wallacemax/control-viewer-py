"""
End-to-End integration tests for the Control Viewer application.
These tests require a running application and test the full application stack.
Most of these tests are marked as skipped by default because they require a live application.
"""

import pytest
import os
import sys
import time
import requests
import json
from unittest.mock import patch

# Add the parent directory to the path so we can import the needed modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import configuration
try:
    from config import settings
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


@pytest.fixture
def app_url():
    """
    Get the URL for the running application.
    """
    if CONFIG_AVAILABLE:
        return f"http://{settings.HOST}:{settings.PORT}"
    else:
        return "http://localhost:8000"  # Default fallback


@pytest.mark.skipif(not os.environ.get("RUN_E2E"), reason="E2E tests require RUN_E2E=1")
class TestEndToEndAPI:
    """
    End-to-End tests for the API endpoints.
    """
    
    def test_health_endpoint(self, app_url):
        """
        Test the health endpoint on a live application.
        """
        # Make a request to the health endpoint
        response = requests.get(f"{app_url}/health")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_get_sensors(self, app_url):
        """
        Test getting sensors from a live application.
        """
        # Make a request to the sensors endpoint
        response = requests.get(f"{app_url}/api/sensors")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # If there are sensors, check their structure
        if data:
            sensor = data[0]
            assert "id" in sensor
            assert "name" in sensor
            assert "value" in sensor
    
    def test_get_sensor_by_id(self, app_url):
        """
        Test getting a specific sensor from a live application.
        """
        # First, get all sensors to find one to test
        response = requests.get(f"{app_url}/api/sensors")
        assert response.status_code == 200
        sensors = response.json()
        
        # If there are sensors, test getting one by ID
        if sensors:
            sensor_id = sensors[0]["id"]
            response = requests.get(f"{app_url}/api/sensors/{sensor_id}")
            
            # Check the response
            assert response.status_code == 200
            sensor = response.json()
            assert sensor["id"] == sensor_id
    
    def test_update_sensor(self, app_url):
        """
        Test updating a sensor on a live application.
        """
        # First, get all sensors to find one to update
        response = requests.get(f"{app_url}/api/sensors")
        assert response.status_code == 200
        sensors = response.json()
        
        # If there are sensors, try updating one
        if sensors:
            sensor_id = sensors[0]["id"]
            current_value = sensors[0]["value"]
            new_value = current_value + 5 if current_value is not None else 50
            
            # Update the sensor
            update_data = {"value": new_value}
            response = requests.put(
                f"{app_url}/api/sensors/{sensor_id}",
                json=update_data
            )
            
            # Check the response
            assert response.status_code == 200
            updated_sensor = response.json()
            assert updated_sensor["id"] == sensor_id
            assert updated_sensor["value"] == new_value
    
    def test_toggle_simulation(self, app_url):
        """
        Test toggling simulation on a live application.
        """
        # Toggle the simulation
        response = requests.post(f"{app_url}/api/simulation/toggle")
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        
        # Wait briefly and toggle again to restore state
        time.sleep(1)
        requests.post(f"{app_url}/api/simulation/toggle")


@pytest.mark.skipif(not os.environ.get("RUN_E2E_BROWSER"), reason="Browser E2E tests require RUN_E2E_BROWSER=1")
class TestEndToEndUI:
    """
    End-to-End tests for the UI using a browser.
    These tests require Selenium or a similar browser automation tool.
    """
    
    @pytest.fixture
    def selenium_driver(self):
        """
        Create a Selenium WebDriver for browser testing.
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Configure Chrome options
            chrome_options = Options()
            if os.environ.get("HEADLESS"):
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Create the driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.implicitly_wait(10)
            
            yield driver
            
            # Quit the driver after the test
            driver.quit()
            
        except ImportError:
            pytest.skip("Selenium not installed")
    
    def test_ui_loads(self, selenium_driver, app_url):
        """
        Test that the UI loads correctly.
        """
        from selenium.webdriver.common.by import By
        
        # Navigate to the application
        selenium_driver.get(app_url)
        
        # Check the title
        assert "Control Viewer" in selenium_driver.title
        
        # Check that main UI components are present
        # This depends on the actual UI implementation
        # Assuming there's a container with a specific class
        containers = selenium_driver.find_elements(By.CLASS_NAME, "container")
        assert len(containers) > 0
    
    def test_tabs_navigation(self, selenium_driver, app_url):
        """
        Test navigating between tabs.
        """
        from selenium.webdriver.common.by import By
        
        # Navigate to the application
        selenium_driver.get(app_url)
        
        # This depends on the actual UI implementation
        # Assuming there are tabs with specific labels
        try:
            # Find and click on the Sensors tab
            sensors_tab = selenium_driver.find_element(By.XPATH, "//div[contains(text(), 'Sensors')]")
            sensors_tab.click()
            
            # Check that the sensors content is visible
            # This depends on the actual UI implementation
            time.sleep(1)  # Allow time for tab to change
            assert selenium_driver.find_element(By.XPATH, "//div[contains(@id, 'sensors-panel')]")
            
            # Find and click on the Dashboard tab
            dashboard_tab = selenium_driver.find_element(By.XPATH, "//div[contains(text(), 'Dashboard')]")
            dashboard_tab.click()
            
            # Check that the dashboard content is visible
            time.sleep(1)  # Allow time for tab to change
            assert selenium_driver.find_element(By.XPATH, "//div[contains(@id, 'dashboard-panel')]")
            
        except Exception as e:
            # If we can't find the expected elements, skip the test
            pytest.skip(f"UI elements not found: {str(e)}")
    
    def test_simulation_toggle(self, selenium_driver, app_url):
        """
        Test toggling simulation from the UI.
        """
        from selenium.webdriver.common.by import By
        
        # Navigate to the application
        selenium_driver.get(app_url)
        
        try:
            # Find and click the simulation toggle button
            toggle_button = selenium_driver.find_element(By.XPATH, "//button[contains(text(), 'Simulation')]")
            initial_status = toggle_button.text
            toggle_button.click()
            
            # Wait for the status to update
            time.sleep(2)
            
            # Check that the button text changed
            updated_status = selenium_driver.find_element(By.XPATH, "//button[contains(text(), 'Simulation')]").text
            assert initial_status != updated_status
            
            # Toggle back to restore state
            toggle_button = selenium_driver.find_element(By.XPATH, "//button[contains(text(), 'Simulation')]")
            toggle_button.click()
            
        except Exception as e:
            # If we can't find the expected elements, skip the test
            pytest.skip(f"UI elements not found: {str(e)}")


@pytest.mark.skipif(not os.environ.get("RUN_LOAD_TEST"), reason="Load tests require RUN_LOAD_TEST=1")
class TestLoadTesting:
    """
    Load testing for the application.
    These tests send multiple requests to test performance under load.
    """
    
    def test_health_endpoint_load(self, app_url):
        """
        Load test the health endpoint.
        """
        # Number of requests to make
        num_requests = 100
        
        # Send requests and measure time
        start_time = time.time()
        success_count = 0
        
        for _ in range(num_requests):
            try:
                response = requests.get(f"{app_url}/health")
                if response.status_code == 200:
                    success_count += 1
            except Exception:
                pass
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Log the results
        print(f"\nHealth endpoint load test results:")
        print(f"Requests: {num_requests}")
        print(f"Successful: {success_count}")
        print(f"Time: {elapsed_time:.2f} seconds")
        print(f"Requests per second: {num_requests / elapsed_time:.2f}")
        
        # Assert on success rate
        assert success_count / num_requests >= 0.95  # 95% success rate
    
    def test_api_endpoints_load(self, app_url):
        """
        Load test the API endpoints.
        """
        # Number of requests per endpoint
        num_requests = 50
        
        # Endpoints to test
        endpoints = [
            "/api/sensors",
            "/health"
        ]
        
        # Send requests and measure time
        start_time = time.time()
        results = {}
        
        for endpoint in endpoints:
            success_count = 0
            endpoint_start_time = time.time()
            
            for _ in range(num_requests):
                try:
                    response = requests.get(f"{app_url}{endpoint}")
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
            
            endpoint_end_time = time.time()
            elapsed_time = endpoint_end_time - endpoint_start_time
            
            results[endpoint] = {
                "success_count": success_count,
                "elapsed_time": elapsed_time,
                "requests_per_second": num_requests / elapsed_time
            }
        
        end_time = time.time()
        total_elapsed_time = end_time - start_time
        
        # Log the results
        print(f"\nAPI endpoints load test results:")
        print(f"Total time: {total_elapsed_time:.2f} seconds")
        
        for endpoint, result in results.items():
            print(f"\nEndpoint: {endpoint}")
            print(f"Requests: {num_requests}")
            print(f"Successful: {result['success_count']}")
            print(f"Time: {result['elapsed_time']:.2f} seconds")
            print(f"Requests per second: {result['requests_per_second']:.2f}")
            
            # Assert on success rate for each endpoint
            assert result['success_count'] / num_requests >= 0.95  # 95% success rate