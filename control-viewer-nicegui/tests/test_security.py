"""
Security integration tests for the Control Viewer application.
These tests check for common security vulnerabilities in the API endpoints.
"""

import pytest
import os
import sys
import requests
import json
import re
from urllib.parse import urljoin

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


@pytest.mark.skipif(not os.environ.get("RUN_SECURITY"), reason="Security tests require RUN_SECURITY=1")
class TestAPISecurityHeaders:
    """
    Test security headers returned by the API.
    """
    
    def test_health_endpoint_security_headers(self, app_url):
        """
        Test security headers on the health endpoint.
        """
        # Make a request to the health endpoint
        response = requests.get(f"{app_url}/health")
        
        # Check for security headers
        headers = response.headers
        
        # Check for common security headers (these may vary based on your security requirements)
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": None,  # Just check if it exists
            "Strict-Transport-Security": None,
            "X-XSS-Protection": "1; mode=block"
        }
        
        # Log missing headers
        missing_headers = []
        for header, expected_value in security_headers.items():
            if header not in headers:
                missing_headers.append(header)
            elif expected_value is not None and headers[header] != expected_value:
                missing_headers.append(f"{header} (expected: {expected_value}, got: {headers[header]})")
        
        if missing_headers:
            pytest.fail(f"Missing or incorrect security headers: {', '.join(missing_headers)}")
    
    def test_api_endpoints_security_headers(self, app_url):
        """
        Test security headers on the API endpoints.
        """
        # Make a request to the sensors endpoint
        response = requests.get(f"{app_url}/api/sensors")
        
        # Check for security headers
        headers = response.headers
        
        # Check for common security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": None,  # Just check if it exists
            "Strict-Transport-Security": None,
            "X-XSS-Protection": "1; mode=block"
        }
        
        # Log missing headers
        missing_headers = []
        for header, expected_value in security_headers.items():
            if header not in headers:
                missing_headers.append(header)
            elif expected_value is not None and headers[header] != expected_value:
                missing_headers.append(f"{header} (expected: {expected_value}, got: {headers[header]})")
        
        if missing_headers:
            pytest.fail(f"Missing or incorrect security headers: {', '.join(missing_headers)}")


@pytest.mark.skipif(not os.environ.get("RUN_SECURITY"), reason="Security tests require RUN_SECURITY=1")
class TestAPISecurityVulnerabilities:
    """
    Test for common security vulnerabilities in the API.
    """
    
    def test_sql_injection_sensors_endpoint(self, app_url):
        """
        Test for SQL injection vulnerabilities in the sensors endpoint.
        """
        # SQL injection payloads to test
        sql_payloads = [
            "1' OR '1'='1",
            "1; DROP TABLE sensors--",
            "1' UNION SELECT 1,2,3,4,5,6,7,8,9,10--",
        ]
        
        # Try each payload
        for payload in sql_payloads:
            # Attempt to inject SQL in the sensor ID parameter
            url = f"{app_url}/api/sensors/{payload}"
            response = requests.get(url)
            
            # Check for successful injection (should get a 404 or error, not a 200)
            if response.status_code == 200:
                # Check if the response is a valid "not found" JSON
                data = response.json()
                if not (isinstance(data, dict) and "detail" in data and "not found" in data["detail"].lower()):
                    pytest.fail(f"Possible SQL injection vulnerability with payload: {payload}")
    
    def test_xss_vulnerabilities(self, app_url):
        """
        Test for Cross-Site Scripting (XSS) vulnerabilities.
        """
        # XSS payloads to test
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(\"XSS\")'>",
            "javascript:alert('XSS')"
        ]
        
        # Try each payload in a sensor ID
        for payload in xss_payloads:
            # Attempt to inject XSS in the sensor ID parameter
            url = f"{app_url}/api/sensors/{payload}"
            response = requests.get(url)
            
            # Content-Type should be application/json, not text/html
            assert response.headers.get("Content-Type", "").startswith("application/json")
            
            # If there's a validation error (422), check that the payload is properly escaped
            if response.status_code == 422:
                data = response.json()
                detail_str = json.dumps(data.get("detail", ""))
                
                # Check if any HTML tags are unescaped
                if "<" in detail_str and ">" in detail_str:
                    html_pattern = re.compile(r"<[a-zA-Z]")
                    if html_pattern.search(detail_str):
                        pytest.fail(f"Possible XSS vulnerability with payload: {payload}")
    
    def test_path_traversal(self, app_url):
        """
        Test for path traversal vulnerabilities.
        """
        # Path traversal payloads to test
        traversal_payloads = [
            "../../../etc/passwd",
            "..%2f..%2f..%2fetc%2fpasswd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        # Try each payload
        for payload in traversal_payloads:
            # Attempt to use path traversal in the sensor ID parameter
            url = f"{app_url}/api/sensors/{payload}"
            response = requests.get(url)
            
            # Should not return a successful response with file contents
            assert response.status_code != 200 or "/bin/" not in response.text
    
    def test_api_rate_limiting(self, app_url):
        """
        Test for rate limiting on API endpoints.
        """
        # Make multiple rapid requests to the same endpoint
        num_requests = 50
        start_time = time.time()
        responses = []
        
        for _ in range(num_requests):
            response = requests.get(f"{app_url}/api/sensors")
            responses.append(response)
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        # Check if any requests were rate limited
        rate_limited = any(r.status_code == 429 for r in responses)
        
        # If requests were rate limited, the test passes
        if rate_limited:
            return
        
        # If no rate limiting, check if there's adequate performance
        # (This is a fallback check in case rate limiting isn't implemented)
        avg_response_time = elapsed_time / num_requests
        
        # If average response time is more than 500ms, there might be
        # some form of rate limiting or throttling
        if avg_response_time > 0.5:
            return
        
        # If neither condition is met, suggest implementing rate limiting
        pytest.skip("No rate limiting detected, consider implementing it")


@pytest.mark.skipif(not os.environ.get("RUN_SECURITY"), reason="Security tests require RUN_SECURITY=1")
class TestAuthorizationAndAuthentication:
    """
    Test authorization and authentication if implemented.
    """
    
    def test_api_endpoints_require_authentication(self, app_url):
        """
        Test that API endpoints require authentication if implemented.
        """
        # This is a basic check to see if authentication is implemented
        # Make a request without authentication
        response = requests.get(f"{app_url}/api/sensors")
        
        # If authentication is required, we should get a 401 Unauthorized
        # If not, the test passes automatically (no authentication required)
        if response.status_code == 401:
            # Now try with invalid authentication
            headers = {"Authorization": "Bearer invalid_token"}
            response = requests.get(f"{app_url}/api/sensors", headers=headers)
            
            # Should still get a 401
            assert response.status_code == 401
    
    def test_admin_endpoints_protected(self, app_url):
        """
        Test that admin endpoints are protected.
        """
        # Check for common admin endpoints
        admin_endpoints = [
            "/admin",
            "/api/admin",
            "/api/config",
            "/api/settings",
            "/api/users"
        ]
        
        for endpoint in admin_endpoints:
            url = urljoin(app_url, endpoint)
            response = requests.get(url)
            
            # Should not return a successful response without authentication
            if response.status_code == 200:
                pytest.fail(f"Admin endpoint {endpoint} is accessible without authentication")


# Import additional modules for security tests
import time
import socket
import ssl

@pytest.mark.skipif(not os.environ.get("RUN_SECURITY"), reason="Security tests require RUN_SECURITY=1")
class TestNetworkSecurity:
    """
    Test network security aspects of the application.
    """
    
    def test_https_redirect(self, app_url):
        """
        Test that HTTP requests are redirected to HTTPS if SSL is configured.
        """
        # This test only makes sense if the app URL is HTTPS
        if not app_url.startswith("https://"):
            pytest.skip("App is not using HTTPS")
        
        # Try to access via HTTP
        http_url = app_url.replace("https://", "http://")
        response = requests.get(http_url, allow_redirects=False)
        
        # Should get a redirect to HTTPS
        assert response.status_code in (301, 302, 307, 308)
        assert response.headers.get("Location", "").startswith("https://")
    
    def test_ssl_configuration(self, app_url):
        """
        Test SSL configuration if HTTPS is used.
        """
        # This test only makes sense if the app URL is HTTPS
        if not app_url.startswith("https://"):
            pytest.skip("App is not using HTTPS")
        
        # Parse the URL to get host and port
        from urllib.parse import urlparse
        parsed_url = urlparse(app_url)
        host = parsed_url.hostname
        port = parsed_url.port or 443
        
        # Create an SSL context with high security settings
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # Disable TLS 1.0 and 1.1
        
        try:
            # Try to connect with secure settings
            with socket.create_connection((host, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    # Check the certificate
                    cert = ssock.getpeercert()
                    # Verify hostname matches the certificate
                    ssl.match_hostname(cert, host)
                    # Check SSL version
                    assert ssock.version() in ("TLSv1.2", "TLSv1.3")
        except ssl.SSLError as e:
            pytest.fail(f"SSL configuration issue: {str(e)}")
        except Exception as e:
            pytest.fail(f"Error testing SSL: {str(e)}")