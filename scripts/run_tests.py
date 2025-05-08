#!/usr/bin/env python3
"""
Test suite driver for CWEB project.
Runs all tests and reports results.

Usage:
    python scripts/run_tests.py [--verbose]
"""

import os
import sys
import unittest
import subprocess
import argparse
import time
from datetime import datetime

# Define colors for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'
BOLD = '\033[1m'

def run_unittest_suite():
    """Run the standard unittest suite."""
    print(f"{BLUE}{BOLD}Running unittest suite...{ENDC}")
    
    # Discover and run all tests
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

def run_script_test(script_path, args=None):
    """Run a test script and return success/failure."""
    if args is None:
        args = []
    
    script_name = os.path.basename(script_path)
    print(f"{BLUE}Running {script_name}...{ENDC}")
    
    cmd = [sys.executable, script_path] + args
    try:
        start_time = time.time()
        result = subprocess.run(cmd, check=False, capture_output=True, text=True)
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"{GREEN}✓ {script_name} passed ({elapsed_time:.2f}s){ENDC}")
            return True
        else:
            print(f"{RED}✗ {script_name} failed ({elapsed_time:.2f}s){ENDC}")
            print(f"{YELLOW}Error output:{ENDC}")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"{RED}✗ {script_name} failed with exception: {str(e)}{ENDC}")
        return False

def run_integration_tests(verbose=False):
    """Run integration tests."""
    print(f"{BLUE}{BOLD}Running integration tests...{ENDC}")
    
    # List of integration test scripts to run
    integration_tests = [
        'scripts/test_neptune_connection.py',
        'scripts/test_titan_embeddings.py',
        'scripts/test_bedrock_embeddings.py'
    ]
    
    results = {}
    for test in integration_tests:
        if os.path.exists(test):
            results[test] = run_script_test(test, ['--dry-run'] if not verbose else [])
        else:
            print(f"{YELLOW}Warning: Test script {test} not found{ENDC}")
            results[test] = False
    
    return results

def run_schema_validation():
    """Run schema validation tests."""
    print(f"{BLUE}{BOLD}Running schema validation...{ENDC}")
    
    # List of schema validation scripts
    schema_scripts = [
        'scripts/create_hyperibis_schema.py',
        'scripts/create_metacog_schema.py',
        'scripts/create_metacog_schema_opencypher.py'
    ]
    
    results = {}
    for script in schema_scripts:
        if os.path.exists(script):
            results[script] = run_script_test(script, ['--validate-only'])
        else:
            print(f"{YELLOW}Warning: Schema script {script} not found{ENDC}")
            results[script] = False
    
    return results

def main():
    """Main function to run all tests."""
    parser = argparse.ArgumentParser(description='Run CWEB test suite')
    parser.add_argument('--verbose', action='store_true', help='Run tests in verbose mode')
    parser.add_argument('--unit-only', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration-only', action='store_true', help='Run only integration tests')
    parser.add_argument('--schema-only', action='store_true', help='Run only schema validation')
    args = parser.parse_args()
    
    print(f"{BOLD}CWEB Test Suite Runner{ENDC}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    all_passed = True
    
    # Run unit tests
    if not args.integration_only and not args.schema_only:
        unit_passed = run_unittest_suite()
        all_passed = all_passed and unit_passed
    
    # Run integration tests
    if not args.unit_only and not args.schema_only:
        integration_results = run_integration_tests(args.verbose)
        all_passed = all_passed and all(integration_results.values())
    
    # Run schema validation
    if not args.unit_only and not args.integration_only:
        schema_results = run_schema_validation()
        all_passed = all_passed and all(schema_results.values())
    
    print("-" * 60)
    if all_passed:
        print(f"{GREEN}{BOLD}All tests passed!{ENDC}")
        return 0
    else:
        print(f"{RED}{BOLD}Some tests failed!{ENDC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
