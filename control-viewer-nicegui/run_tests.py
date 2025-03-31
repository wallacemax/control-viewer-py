#!/usr/bin/env python3
"""
Script to run all tests for the Control Viewer application.
This script provides a convenient way to run different test categories.
"""
import os
import sys
import argparse
import subprocess

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run tests for the Control Viewer application.")
   
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--ui", action="store_true", help="Run UI tests")
    parser.add_argument("--database", action="store_true", help="Run database tests")
    parser.add_argument("--simulation", action="store_true", help="Run simulation tests")
    parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--docker", action="store_true", help="Run Docker tests")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
   
    return parser.parse_args()

def run_tests(test_files, env_vars=None, coverage=False, verbose=False):
    """Run pytest with the specified test files and environment variables."""
    if not test_files:
        print("No test files specified")
        return 0
   
    # Prepare environment variables
    env = os.environ.copy()
    if env_vars:
        env.update(env_vars)
   
    # Prepare command
    cmd = ["pytest"]
   
    # Add verbosity if requested
    if verbose:
        cmd.append("-v")
   
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term", "--cov-report=html"])
   
    # Filter out empty or None values from test_files
    valid_test_files = [f for f in test_files if f]
    
    # Add test files to command
    if valid_test_files:
        cmd.extend(valid_test_files)
    
    # Print the command we're about to run
    print(f"Running command: {' '.join(cmd)}")
    
    # Use shell=True on Windows to handle paths with spaces correctly
    use_shell = sys.platform.startswith('win')
    
    # Convert list to string command if using shell
    if use_shell:
        # For Windows with shell=True, we need to properly quote paths with spaces
        shell_cmd = "pytest"
        if verbose:
            shell_cmd += " -v"
        if coverage:
            shell_cmd += " --cov=. --cov-report=term --cov-report=html"
        for file in valid_test_files:
            # Quote the path if it has spaces
            if " " in file:
                shell_cmd += f' "{file}"'
            else:
                shell_cmd += f" {file}"
        print(f"Running shell command: {shell_cmd}")
        result = subprocess.run(shell_cmd, shell=True, env=env)
    else:
        # For non-Windows systems, use the list approach
        result = subprocess.run(cmd, env=env)
   
    return result.returncode

def main():
    """Main function."""
    print("Starting test runner...")

    #debug info
    # Print current directory and list files to help diagnose
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    print("Files in current directory:")
    for file in os.listdir(current_dir):
        if file.endswith('.py'):
            print(f"  - {file}")
    
    # Check for a tests directory
    tests_dir = os.path.join(current_dir, "tests")
    if os.path.isdir(tests_dir):
        print(f"Found tests directory: {tests_dir}")
        print("Files in tests directory:")
        for file in os.listdir(tests_dir):
            if file.endswith('.py'):
                print(f"  - {file}")
    else:
        print("No tests directory found")
    
    # Try running pytest directly with verbosity to see its discovery process
    print("\nTrying to run pytest with verbosity to see discovery process:")
    subprocess.run(["pytest", "-v", "--collect-only"])

    args = parse_args()
   
    # Determine which tests to run
    test_files = []
    env_vars = {}
   
    # If no specific tests are requested, default to running unit tests
    if not any([args.all, args.unit, args.integration, args.api, args.ui,
                args.database, args.simulation, args.e2e, args.security, args.docker]):
        args.unit = True
   
    # Get the current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Look for test files in the current directory and tests directory
    tests_dir = os.path.join(current_dir, "tests")
    if os.path.isdir(tests_dir):
        print(f"Found tests directory: {tests_dir}")
    else:
        tests_dir = current_dir
        print(f"No tests directory found, looking for tests in current directory")
   
    # Collect test files based on arguments
    if args.all or args.unit:
        # Use a simple pattern for unit tests
        test_files.append("test_*.py")
        print("Added unit test pattern: test_*.py")
   
    if args.all or args.integration:
        integration_test = os.path.join(tests_dir, "test_integration.py")
        if os.path.exists(integration_test):
            test_files.append(integration_test)
            print(f"Added integration test: {integration_test}")
        else:
            print(f"Warning: Integration test file not found at {integration_test}")
   
    if args.all or args.api:
        api_test = os.path.join(tests_dir, "test_api.py")
        if os.path.exists(api_test):
            test_files.append(api_test)
            print(f"Added API test: {api_test}")
        else:
            print(f"Warning: API test file not found at {api_test}")
   
    if args.all or args.ui:
        ui_test = os.path.join(tests_dir, "test_ui.py")
        if os.path.exists(ui_test):
            test_files.append(ui_test)
            print(f"Added UI test: {ui_test}")
        else:
            print(f"Warning: UI test file not found at {ui_test}")
   
    if args.all or args.database:
        db_test = os.path.join(tests_dir, "test_database.py")
        if os.path.exists(db_test):
            test_files.append(db_test)
            print(f"Added database test: {db_test}")
        else:
            print(f"Warning: Database test file not found at {db_test}")
   
    if args.all or args.simulation:
        sim_test = os.path.join(tests_dir, "test_simulation.py")
        if os.path.exists(sim_test):
            test_files.append(sim_test)
            print(f"Added simulation test: {sim_test}")
        else:
            print(f"Warning: Simulation test file not found at {sim_test}")
   
    if args.all or args.e2e:
        e2e_test = os.path.join(tests_dir, "test_e2e.py")
        if os.path.exists(e2e_test):
            test_files.append(e2e_test)
            print(f"Added E2E test: {e2e_test}")
        else:
            print(f"Warning: E2E test file not found at {e2e_test}")
        env_vars["RUN_E2E"] = "1"
   
    if args.all or args.security:
        security_test = os.path.join(tests_dir, "test_security.py")
        if os.path.exists(security_test):
            test_files.append(security_test)
            print(f"Added security test: {security_test}")
        else:
            print(f"Warning: Security test file not found at {security_test}")
        env_vars["RUN_SECURITY"] = "1"
   
    print(f"Test files to run: {test_files}")
   
    # Run the tests
    return run_tests(
        test_files=test_files,
        env_vars=env_vars,
        coverage=args.coverage,
        verbose=args.verbose
    )

if __name__ == "__main__":
    sys.exit(main())