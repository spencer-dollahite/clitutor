"""Unit tests for fleet monitor."""

import unittest
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor import check_host, get_status


class TestCheckHost(unittest.TestCase):
    """Test host connectivity checks."""

    def test_localhost_ssh(self):
        """SSH on localhost should be running."""
        result = check_host("localhost", 22)
        self.assertTrue(result)

    def test_localhost_http(self):
        """HTTP on localhost should be running (nginx)."""
        result = check_host("localhost", 80)
        self.assertTrue(result)

    def test_unreachable_host(self):
        """Unreachable host should return False."""
        result = check_host("192.0.2.1", 22)  # TEST-NET, always unreachable
        self.assertFalse(result)


class TestGetStatus(unittest.TestCase):
    """Test status report generation."""

    def test_localhost_status(self):
        """Localhost should report as online."""
        status = get_status("localhost")
        self.assertEqual(status["host"], "localhost")
        self.assertIn(status["overall"], ["online", "degraded", "offline"])
        self.assertIn("timestamp", status)


if __name__ == "__main__":
    unittest.main()
