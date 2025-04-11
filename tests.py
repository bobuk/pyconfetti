#!/usr/bin/env python3
"""
Simple test script for PyConfetti.
"""

import unittest

from pyconfetti import ConfettiError, ConfettiOptions, parse


class PyConfettiTests(unittest.TestCase):
    """Basic tests for PyConfetti."""

    def test_parse_simple_config(self):
        """Test parsing a simple configuration."""
        config = """
        server {
            host localhost
            port 8080
        }
        """
        unit = parse(config)
        self.assertEqual(len(unit.root.subdirectives), 1)
        self.assertEqual(unit.root.subdirectives[0].arguments[0].value, "server")

    def test_parse_with_comments(self):
        """Test parsing a configuration with comments."""
        config = """
        # This is a comment
        server {
            host localhost  # Host directive
            port 8080       # Port directive
        }
        """
        unit = parse(config)
        self.assertEqual(len(unit.root.subdirectives), 1)
        self.assertEqual(len(unit.comments), 3)  # Including inline comments

    def test_parse_nested_blocks(self):
        """Test parsing nested blocks."""
        config = """
        server {
            host localhost
            port 8080

            ssl {
                enabled true
                cert "/path/to/cert.pem"
            }
        }
        """
        unit = parse(config)
        self.assertEqual(len(unit.root.subdirectives), 1)
        server = unit.root.subdirectives[0]
        self.assertEqual(len(server.subdirectives), 1)

        # Find SSL directive
        ssl_found = False
        for subdir in server.subdirectives:
            for i, arg in enumerate(subdir.arguments):
                if arg.value == "ssl":
                    ssl_found = True
                    break
        self.assertTrue(ssl_found)

    def test_parse_error(self):
        """Test parsing error handling."""
        config = """
        server {
            host localhost
            port 8080
        """  # Missing closing brace
        with self.assertRaises(ConfettiError):
            parse(config)

    def test_custom_options(self):
        """Test parsing with custom options."""
        config = """
        /* This is a C-style comment */
        server {
            host localhost
            port 8080
        }
        """
        # This should fail without c_style_comments
        with self.assertRaises(ConfettiError):
            parse(config)

        # This should pass with c_style_comments
        options = ConfettiOptions(c_style_comments=True)
        unit = parse(config, options)
        self.assertEqual(len(unit.root.subdirectives), 1)


if __name__ == "__main__":
    unittest.main()
