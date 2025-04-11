#!/usr/bin/env python3
"""
Advanced example demonstrating PyConfetti mapper with enum support, nested objects,
lists, and optional fields.
"""

from dataclasses import field
from enum import Enum, auto
from typing import List, Optional

from pyconfetti import MappingError, confetti, dump_confetti, load_confetti


# Define an enum for log levels
class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


# Define an enum with auto() values
class Environment(Enum):
    DEV = auto()
    STAGING = auto()
    PRODUCTION = auto()


@confetti  # type: ignore
class LoggingConfig:
    level: LogLevel = LogLevel.INFO
    file_path: Optional[str] = None
    max_size_mb: int = 10
    backup_count: int = 3


@confetti  # type: ignore
class DatabaseConnection:
    host: str
    port: int
    username: str
    password: str
    ssl_enabled: bool = False


@confetti  # type: ignore
class CacheConfig:
    enabled: bool = True
    ttl_seconds: int = 300
    max_items: int = 1000


@confetti(name="db_pool")  # type: ignore
# Using custom name for the confetti directive
class DatabasePool:
    min_connections: int = 5
    max_connections: int = 20
    timeout_seconds: int = 30


@confetti  # type: ignore
class ApiEndpoint:
    path: str
    method: str = "GET"
    rate_limit: Optional[int] = None


@confetti  # type: ignore
class AppConfig:
    name: str
    environment: Environment = Environment.DEV
    port: int = 8080
    database: DatabaseConnection
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    cache: Optional[CacheConfig] = None
    db_pool: Optional[DatabasePool] = None
    allowed_origins: List[str] = field(default_factory=list)  # List support
    api_endpoints: List[ApiEndpoint] = field(default_factory=list)  # List of objects


def main() -> None:
    # Example Confetti configuration
    config_text = """
    app_config {
        name "My Advanced App"
        environment PRODUCTION
        port 9000

        database {
            host db.example.com
            port 5432
            username dbuser
            password secret123
            ssl_enabled true
        }

        logging {
            level debug
            file_path "/var/log/myapp.log"
            max_size_mb 20
        }

        cache {
            enabled true
            ttl_seconds 600
            max_items 2000
        }

        db_pool {
            min_connections 10
            max_connections 50
        }

        allowed_origins "http://localhost:3000,https://example.com"

        api_endpoints {
            path "/api/users"
            method "GET"
            rate_limit 100
        }

        api_endpoints {
            path "/api/orders"
            method "POST"
        }
    }
    """

    try:
        # Parse the configuration into a Python object
        config = load_confetti(config_text, AppConfig)

        # Access the configuration as Python objects
        print("=== Loaded Application Configuration ===")
        print(f"Name: {config.name}")
        print(f"Environment: {config.environment.name}")
        print(f"Port: {config.port}")

        print("\n=== Database Configuration ===")
        print(f"Host: {config.database.host}")
        print(f"Port: {config.database.port}")
        print(f"Username: {config.database.username}")
        print(f"SSL Enabled: {config.database.ssl_enabled}")

        print("\n=== Logging Configuration ===")
        print(f"Level: {config.logging.level.value}")
        print(f"File Path: {config.logging.file_path}")

        print("\n=== Cache Configuration ===")
        if config.cache:
            print(f"Enabled: {config.cache.enabled}")
            print(f"TTL: {config.cache.ttl_seconds} seconds")
        else:
            print("Cache not configured")

        print("\n=== Database Pool ===")
        if config.db_pool:
            print(f"Min Connections: {config.db_pool.min_connections}")
            print(f"Max Connections: {config.db_pool.max_connections}")

        print("\n=== Allowed Origins ===")
        for origin in config.allowed_origins:
            print(f"- {origin}")

        print("\n=== API Endpoints ===")
        for endpoint in config.api_endpoints:
            print(f"- {endpoint.method} {endpoint.path} ")
            if endpoint.rate_limit:
                print(f"  Rate Limit: {endpoint.rate_limit} req/min")

        # Convert back to Confetti format
        regenerated_config = dump_confetti(config)
        print("\n=== Regenerated Confetti Configuration ===")
        print(regenerated_config)

    except MappingError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
