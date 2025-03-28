# Control Viewer Test Suite

This document provides an overview of the comprehensive test suite created for the Control Viewer application.

## Test Categories

The test suite is organized into the following categories:

### 1. Core Integration Tests (`test_integration.py`)
Tests the core integration points of the application, including the FastAPI application startup, endpoint functionality, and lifecycle management.

### 2. API Tests (`test_api.py`)
Tests the API endpoints, request handling, response formatting, and error handling.

### 3. UI Tests (`test_ui.py`)
Tests the NiceGUI UI components, rendering, event handling, and UI-API integration.

### 4. Database Tests (`test_database.py`)
Tests database operations, data persistence, and interaction with the database layer.

### 5. Simulation Tests (`test_simulation.py`)
Tests the simulation functionality including data generation and control mechanisms.

### 6. Configuration Tests (`test_config.py`)
Tests configuration loading, environment variable handling, and application settings.

### 7. NiceGUI Integration Tests (`test_nicegui.py`)
Tests specific to NiceGUI integration with FastAPI.

### 8. End-to-End Tests (`test_e2e.py`)
End-to-end tests that verify the entire application stack works together.

### 9. Security Tests (`test_security.py`)
Tests security aspects including headers, authentication, and vulnerability checks.

### 10. Docker Deployment Tests (`test_docker.py`)
Tests Docker image building, container running, and deployment.

## Test Setup

The test suite uses the following key components:

- **pytest**: The main testing framework
- **pytest-asyncio**: For testing asynchronous code
- **httpx**: For making HTTP requests to test the API
- **unittest.mock**: For mocking dependencies and isolating components
- **conftest.py**: Contains shared fixtures and test configuration
- **run_tests.py**: A utility script to run different test categories

## Running Tests

### Basic Usage

Run all tests:
```bash
python run_tests.py --all
```

Run specific test categories:
```bash
python run_tests.py --integration --api
```

Run with coverage:
```bash
python run_tests.py --all --coverage
```

### Specialized Test Categories

For End-to-End tests (requires a running application):
```bash
python run_tests.py --e2e
```

For Security tests:
```bash
python run_tests.py --security
```

For Docker tests (requires Docker):
```bash
python run_tests.py --docker
```

## Test Structure

Each test file follows a similar structure:

1. **Test Fixtures**: Define the necessary test fixtures at the top
2. **Test Classes**: Group related tests into classes
3. **Test Functions**: Individual test cases within classes
4. **Mocks and Patches**: Mock external dependencies to isolate components
5. **Assertions**: Verify the expected behavior

## Continuous Integration

The test suite is integrated with GitHub Actions to run tests automatically on push and pull requests. The workflow is defined in `.github/workflows/tests.yml`.

The CI workflow runs:
1. Unit and integration tests on multiple Python versions
2. Security checks using Bandit and Safety
3. Docker image building and testing

## Writing New Tests

When adding new features, follow these guidelines for writing tests:

1. Use the appropriate test file based on the feature category
2. Create descriptive test functions with clear assertions
3. Mock external dependencies to isolate the component being tested
4. Use fixtures from `conftest.py` where applicable
5. Handle both successful and error cases
6. Add browser-based tests for UI changes where necessary

## Test Coverage

The test suite is designed to achieve high code coverage across the application. To view the coverage report:

```bash
python run_tests.py --all --coverage
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Troubleshooting

If tests are failing, check the following:

1. **Environment Issues**: Make sure all dependencies are installed
2. **Configuration**: Verify environment variables and settings
3. **Mock Setup**: Check that mocks are configured correctly
4. **Async Code**: Use the appropriate async/await syntax for testing async functions
5. **API Changes**: Update tests when API endpoints or parameters change

For Docker and E2E test failures, ensure the application is running correctly outside of tests first.