#!/usr/bin/env python3
"""
Example usage of the Confetti Python parser.
"""

from typing import List, Optional

from pyconfetti import Argument, Comment, ElementType, parse, pretty_print, walk


def parse_example(config_text: str) -> None:
    """Demonstrate the parse API."""
    print("=== Parse API Example ===")

    # Parse the configuration
    unit = parse(config_text)

    # Pretty print the parsed configuration
    pretty_print(unit)


def walk_example(config_text: str) -> None:
    """Demonstrate the walk API."""
    print("\n=== Walk API Example ===")

    depth = 0

    def callback(element_type: ElementType, arguments: List[Argument], comment: Optional[Comment]) -> bool:
        nonlocal depth

        if element_type == ElementType.COMMENT and comment is not None:
            print(f"# {comment.text}")
            return True

        elif element_type == ElementType.DIRECTIVE:
            indent = "    " * depth
            args_str = " ".join(arg.value for arg in arguments)
            print(f"{indent}{args_str}")
            return True

        elif element_type == ElementType.BLOCK_ENTER:
            indent = "    " * depth
            print(f"{indent}{{")
            depth += 1
            return True

        elif element_type == ElementType.BLOCK_LEAVE:
            depth -= 1
            indent = "    " * depth
            print(f"{indent}}}")
            return True

        return True

    # Walk through the configuration
    walk(config_text, callback)


if __name__ == "__main__":
    # Example configuration
    config = """
    # This is a comment
    server {
        host localhost
        port 8080

        ssl {
            enabled true
            cert "/path/to/cert.pem"
        }
    }

    database "primary" {
        url "postgres://user:pass@localhost:5432/db"
        max_connections 100
    }
    """

    # Demonstrate parse API
    parse_example(config)

    # Demonstrate walk API
    walk_example(config)
