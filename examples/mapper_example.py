#!/usr/bin/env python3
"""
Example demonstrating the use of PyConfetti mapper module for mapping between
Confetti configurations and Python dataclasses.
"""

from typing import Optional

from pyconfetti import MappingError, confetti, dump_confetti, load_confetti


# Define your classes with type annotations
@confetti  # type: ignore
class Database:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None


@confetti  # type: ignore
class WebServer:
    host: str
    dbname: str
    port: int = 8080


@confetti  # type: ignore
class Config:
    database: Database
    server: WebServer


def main() -> None:
    # Example Confetti configuration
    config_text = """
    config {
        database {
            host localhost
            port 5432
            username admin
        }

        server {
            host 127.0.0.1
            dbname myapp
        }
    }
    """

    # Load the configuration into a Config object
    try:
        config = load_confetti(config_text, Config)

        # Access the configuration as regular Python objects
        print("Loaded configuration:")
        print(f"Database: {config.database.host}:{config.database.port}")
        print(f"Database username: {config.database.username}")
        print(f"Server: {config.server.host}, DB: {config.server.dbname}, Port: {config.server.port}")

        # Create a configuration programmatically
        new_config = Config(  # type: ignore
            database=Database(host="localhost", port=5433, username="postgres"),  # type: ignore
            server=WebServer(host="0.0.0.0", dbname="newapp", port=9000),  # type: ignore
        )

        # Convert back to Confetti
        new_config_text = dump_confetti(new_config)
        print("\nGenerated Confetti configuration:")
        print(new_config_text)

    except MappingError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
