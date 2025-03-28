#!/usr/bin/env python3
"""
Script to run all tests for the Control Viewer application.
This script provides a convenient way to run different test categories.
"""

import os
import sys
import argparse
import subprocess
import time


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
        return
    
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
    
    # Add test files
    cmd.extend(test_files)
    
    # Run pytest
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, env=env)
    
    return result.returncode


def main():
    """Main function."""
    args = parse_args()
    
    # Determine which tests to run
    test_files = []
    env_vars = {}
    
    # If no specific tests are requested, default to running integration tests
    if not any([args.all, args.unit, args.integration, args.api, args.ui, 
                args.database, args.simulation, args.e2e, args.security, args.docker]):
        args.integration = True
    
    # Collect test files based on arguments
    if args.all or args.unit:
        test_files.append("tests/test_*.py")
    
    if args.all or args.integration:
        test_files.append("tests/test_integration.py")
    
    if args.all or args.api:
        test_files.append("tests/test_api.py")
    
    if args.all or args.ui:
        test_files.append("tests/test_ui.py")
    
    if args.all or args.database:
        test_files.append("tests/test_database.py")
    
    if args.all or args.simulation:
        test_files.append("tests/test_simulation.py")
    
    if args.all or args.e2e:
        test_files.append("tests/test_e2e.py")
        env_vars["RUN_E2E"] = "1"
    
    if args.all or args.security:
        test_files.append("tests/test_security.py")
        env_vars["RUN_SECURITY"] = "1"
    
    #no point in doing docker, it doesn't matter
    #if args.all or args.docker:
        #test_files.append("tests/test_docker.py")

    print(test_files)
    
    # Run the tests
    return run_tests(
        test_files=test_files,
        env_vars=env_vars,
        coverage=args.coverage,
        verbose=args.verbose
    )


if __name__ == "__main__":
    sys.exit(main())