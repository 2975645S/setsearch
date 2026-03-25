"""
Test runner for SetSearch Django application.

This module provides utilities for running tests with proper Django setup.
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings for testing
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wad.settings')

# Set up minimal environment variables if not set
os.environ.setdefault('SECRET_KEY', 'test-secret-key-for-testing-only')
os.environ.setdefault('DOMAIN', 'test.example.com')

# Initialize Django
django.setup()

def run_tests():
    """Run all tests for the SetSearch application."""
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["setsearch.tests"])
    return failures

if __name__ == "__main__":
    failures = run_tests()
    sys.exit(bool(failures))