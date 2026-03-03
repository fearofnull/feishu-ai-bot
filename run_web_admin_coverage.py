#!/usr/bin/env python
"""
Quick script to run web admin tests with coverage reporting
"""
import subprocess
import sys

def main():
    """Run web admin tests with coverage"""
    print("Running web admin tests with coverage...")
    print("=" * 60)
    
    # Run tests with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_web_admin.py",
        "tests/test_web_admin_errors.py",
        "tests/test_web_admin_error_scenarios.py",
        "tests/test_web_admin_logging.py",
        # Skip property tests for quick coverage check (they take too long)
        # "tests/test_web_admin_properties.py",
        "--cov=feishu_bot/web_admin",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure
        "--maxfail=5"  # Stop after 5 failures
    ]
    
    result = subprocess.run(cmd, capture_output=False)
    
    print("\n" + "=" * 60)
    if result.returncode == 0:
        print("✓ All tests passed!")
        print("Coverage report generated in htmlcov/index.html")
    else:
        print(f"✗ Tests failed with exit code {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
