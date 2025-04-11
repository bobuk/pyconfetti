#!/usr/bin/env python3
"""
pyconfetti - A Python parser for the Confetti configuration language.
"""

from .mapper import (
    MappingError,
    confetti,
    dump_confetti,
    dump_confetti_file,
    load_confetti,
    load_confetti_file,
)
from .pyconfetti import (
    Argument,
    Comment,
    ConfettiError,
    ConfettiOptions,
    ConfettiUnit,
    Directive,
    ElementType,
    Parser,
    Scanner,
    SyntaxError,
    Walker,
    parse,
    pretty_print,
    print_directive,
    walk,
)

__version__ = "0.1.0"

__all__ = [
    # Core parser
    "Argument",
    "Comment",
    "ConfettiError",
    "ConfettiOptions",
    "ConfettiUnit",
    "Directive",
    "ElementType",
    "Parser",
    "Scanner",
    "SyntaxError",
    "Walker",
    "parse",
    "pretty_print",
    "print_directive",
    "walk",
    # Mapper
    "confetti",
    "load_confetti",
    "load_confetti_file",
    "dump_confetti",
    "dump_confetti_file",
    "MappingError",
]
