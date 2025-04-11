# 🎉 PyConfetti 🎉

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Unlicense](https://img.shields.io/badge/license-Unlicense-blue.svg)](http://unlicense.org/)

> *"Because config files should be as fun as throwing confetti!"* 🎊

A pure Python parser for the [**Confetti**](https://github.com/hgs3/confetti/) configuration language - a simple, flexible, and expressive configuration syntax that makes your config files look like a party! 🥳

## ✨ Features

- 🚀 **Zero dependencies** - just plain Python!
- 🧰 **uv compatible** - works perfectly with modern Python tooling!
- 🔍 **Full parsing support** for directives, arguments, subdirectives, and comments
- 🛡️ **Robust error handling** with helpful error messages
- 🧩 **Two convenient APIs**: parse and walk
- 🔄 **Bidirectional support** for reading AND writing configs
- 📝 **Triple-quoted strings** for multiline values
- 💪 **Well-typed** with complete type annotations

## 🚀 Installation

```bash
uv pip install pyconfetti

# Or install from source
git clone https://github.com/yourusername/pyconfetti.git
cd pyconfetti
uv pip install -e .
```

## 🎯 Quick Start

### Parsing a Confetti Configuration

```python
from pyconfetti import parse, pretty_print

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
"""

# Parse the configuration
unit = parse(config)

# Access the parsed data
server_directive = unit.root.subdirectives[0]

# Iterate through arguments in subdirectives
host_value = None
port_value = None

for subdir in server_directive.subdirectives:
    for i, arg in enumerate(subdir.arguments):
        if arg.value == "host" and i+1 < len(subdir.arguments):
            host_value = subdir.arguments[i+1].value  # "localhost"
        if arg.value == "port" and i+1 < len(subdir.arguments):
            port_value = subdir.arguments[i+1].value  # "8080"

print(f"Host: {host_value}, Port: {port_value}")

# Pretty print the parsed configuration
pretty_print(unit)
```

### Walking Through a Configuration

```python
from pyconfetti import walk, ElementType

def callback(element_type, arguments, comment):
    if element_type == ElementType.COMMENT:
        print(f"Found comment: {comment.text}")
    elif element_type == ElementType.DIRECTIVE:
        print(f"Found directive with arguments: {[arg.value for arg in arguments]}")
    elif element_type == ElementType.BLOCK_ENTER:
        print("Entering block")
    elif element_type == ElementType.BLOCK_LEAVE:
        print("Leaving block")
    return True  # Continue walking

# Walk through the configuration
walk(config, callback)
```

## 🎭 Why Confetti?

[Confetti](https://github.com/hgs3/confetti/) is a configuration language that looks like NGINX config but is more flexible.
Based on the [original C implementation](https://github.com/hgs3/confetti/), this pure Python parser offers full compatibility with the Confetti specification. It's perfect when:

- YAML is too space-sensitive for you 😬
- JSON doesn't support comments 🙄
- TOML feels too INI-like 😴
- XML makes you want to cry 😭

Confetti strikes the perfect balance between readability, expressiveness, and simplicity! ✨

## 🧩 Syntax Example

For more detailed information about the Confetti syntax, check out the [official Confetti specification](https://confetti.hgs3.me/specification/)

```
# This is a comment

# Basic directives
server_name "my-awesome-app.com";
port 8080;

# Blocks with subdirectives
database {
    url "postgres://user:password@localhost:5432/mydb"
    pool_size 10
    timeout 30
}

# Multiple arguments
allowed_origins "http://localhost:3000" "https://example.com";

# Triple-quoted strings for multiline content
description """
    This is a multi-line description
    that spans several lines
    without needing escapes
""";

# Nested blocks
logging {
    level "info"

    file {
        path "/var/log/app.log"
        rotate true
        max_size "10MB"
    }
}
```

## 🗺️ Using the Mapper

PyConfetti's mapper module provides a simple way to map between Confetti configurations and Python dataclasses:

```python
from typing import Optional
from pyconfetti import confetti, load_confetti, dump_confetti

# Define your classes with type annotations
@confetti
class Database:
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None

@confetti
class WebServer:
    host: str
    dbname: str
    port: int = 8080

@confetti
class Config:
    database: Database
    server: WebServer

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
config = load_confetti(config_text, Config)

# Access the configuration as regular Python objects
print(f"Database: {config.database.host}:{config.database.port}")
print(f"Server: {config.server.host}:{config.server.port}")

# Create a new configuration programmatically
new_config = Config(
    database=Database(host="localhost", port=5433, username="postgres"),
    server=WebServer(host="0.0.0.0", dbname="newapp", port=9000),
)

# Convert back to Confetti
new_config_text = dump_confetti(new_config)
```

## 🛠️ Advanced Usage

### Custom Configuration Options

```python
from pyconfetti import parse, ConfettiOptions

# Create custom options
options = ConfettiOptions(
    max_depth=50,               # Maximum nesting depth
    allow_bidi=True,            # Allow bidirectional Unicode control characters
    c_style_comments=True,      # Support C-style comments (/* ... */)
    expression_arguments=True   # Enable expression evaluation in arguments
)

# Parse with custom options
unit = parse(config_text, options)
```

### Building Configurations Programmatically

```python
from pyconfetti import Directive, Argument, ConfettiUnit, pretty_print

# Create directives and arguments
server = Directive()
server.arguments.append(Argument(value="server", offset=0, length=6))

host = Directive()
host.arguments.append(Argument(value="host", offset=0, length=4))
host.arguments.append(Argument(value="localhost", offset=0, length=9))

port = Directive()
port.arguments.append(Argument(value="port", offset=0, length=4))
port.arguments.append(Argument(value="8080", offset=0, length=4))

# Add subdirectives
server.subdirectives.extend([host, port])

# Create a configuration unit
unit = ConfettiUnit()
unit.root.subdirectives.append(server)

# Pretty print the configuration
pretty_print(unit)
```

## 🔍 Error Handling

PyConfetti provides detailed error messages to help you debug configuration issues:

```python
from pyconfetti import parse, ConfettiError

try:
    unit = parse(invalid_config)
except ConfettiError as e:
    print(f"Configuration error: {e}")
    # Handle the error appropriately
```

## 💻 Development

PyConfetti has no runtime dependencies, so you can start developing right away!

```bash
# Clone the repository
git clone https://github.com/yourusername/pyconfetti.git
cd pyconfetti

# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
python run_test_suite.py
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- 🐛 Report bugs
- 💡 Suggest features
- 🔧 Submit pull requests
- 📖 Improve documentation

For questions and discussions about the Confetti format itself, please visit the [original Confetti repository](https://github.com/hgs3/confetti/).

## 📄 License

This project is licensed under the Unlicense - dedicated to the public domain. See the LICENSE file for details.

---

Made with ❤️ and a handful of confetti! 🎊
