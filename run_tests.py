"""
Test runner script for System Performance Monitor
This script provides a convenient way to run tests with various options.
"""
import subprocess
import argparse
import sys
import os
from enum import Enum


class TestType(Enum):
    ALL = "all"
    UNIT = "unit"
    INTEGRATION = "integration"
    API = "api"
    DB = "db"
    MONITOR = "monitor"
    METRICS = "metrics"


def run_tests(test_type=TestType.ALL, verbose=False, coverage=False):
    """Run the tests based on the given parameters"""
    # Set up base command
    cmd = ["pytest"]

    # Add verbosity if requested
    if verbose:
        cmd.append("-v")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=app", "--cov-report", "term-missing"])
    
    # Add specific test markers if not running all tests
    if test_type != TestType.ALL:
        cmd.extend(["-m", test_type.value])
    
    # Run the command
    result = subprocess.run(cmd, shell=True)
    
    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests for System Performance Monitor")
    
    parser.add_argument(
        "--type", 
        type=str,
        choices=[t.value for t in TestType],
        default=TestType.ALL.value,
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Increase verbosity"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true",
        help="Generate coverage report"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("=" * 80)
    print(f"Running {args.type.upper()} tests for System Performance Monitor")
    if args.verbose:
        print("Verbose mode: ON")
    if args.coverage:
        print("Coverage reporting: ON")
    print("=" * 80)
    
    # Run tests
    exit_code = run_tests(
        test_type=TestType(args.type),
        verbose=args.verbose,
        coverage=args.coverage
    )
    
    # Exit with the test result code
    sys.exit(exit_code)
