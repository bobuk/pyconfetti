#!/usr/bin/env python3
"""
PyConfetti Mapper - High-level abstraction for mapping Confetti configurations to Python objects.

This module provides decorators and functions to easily convert between Confetti configuration files
and Python classes with type annotations.
"""

import dataclasses
import inspect
from dataclasses import is_dataclass
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union, cast, get_args, get_origin, get_type_hints, overload

from .pyconfetti import Argument, ConfettiError, ConfettiUnit, Directive
from .pyconfetti import parse as parse_confetti

# Type variables for generics
T = TypeVar("T")
C = TypeVar("C")  # Class type for use with classes and instances

# Registry to keep track of confetti-mapped classes
_CONFETTI_CLASSES: Dict[str, Type[Any]] = {}


class MappingError(ConfettiError):
    """Error raised when there is a problem mapping Confetti to Python objects or vice versa."""

    pass


def _convert_value(value: str, target_type: Type[T]) -> T:
    """Convert a string value to the target type."""
    # Handle Union types (including Optional)
    origin = get_origin(target_type)
    if origin is Union:
        args = get_args(target_type)
        # Handle Optional (Union with NoneType)
        if type(None) in args:
            if value.lower() in ("none", "null"):
                return cast(T, None)
            # Try with the other type
            for arg in args:
                if arg is not type(None):  # Skip NoneType
                    return _convert_value(value, arg)  # type: ignore

        # Try each type in the Union
        for arg in args:
            try:
                return _convert_value(value, arg)  # type: ignore
            except (ValueError, TypeError):
                continue
        raise MappingError(f"Could not convert '{value}' to any of {args}")

    # Handle Enums
    if inspect.isclass(target_type) and issubclass(target_type, Enum):
        # Try to find by name or value
        try:
            return target_type[value]  # type: ignore
        except KeyError:
            # Try to match by value
            for enum_item in target_type:  # type: ignore
                if str(enum_item.value) == value:
                    return cast(T, enum_item)
            raise MappingError(f"No matching enum value '{value}' in {target_type.__name__}")

    # Handle basic types
    if target_type is bool:
        return cast(T, value.lower() in ("true", "yes", "1", "on"))
    elif target_type is int:
        return cast(T, int(value))
    elif target_type is float:
        return cast(T, float(value))
    elif target_type is str:
        return cast(T, value)
    elif target_type is list or target_type is List:
        # For lists without specific types, just return a list with the string
        return cast(T, [value])
    elif origin is list or origin is List:
        # For lists with specific types like List[int], convert the element
        elem_type = get_args(target_type)[0]
        # Split by commas if it's a comma-separated list
        if "," in value:
            result = [_convert_value(item.strip(), elem_type) for item in value.split(",")]
            return cast(T, result)
        # Otherwise, just return a single-element list
        return cast(T, [_convert_value(value, elem_type)])

    # If it's a registered confetti class, it should be handled elsewhere
    if hasattr(target_type, "__name__") and target_type.__name__ in _CONFETTI_CLASSES:
        raise MappingError(f"Nested class {target_type.__name__} should be handled by a directive, not an argument")

    # Last resort: try direct conversion
    try:
        return target_type(value)  # type: ignore
    except (ValueError, TypeError) as e:
        raise MappingError(f"Could not convert '{value}' to {getattr(target_type, '__name__', str(target_type))}: {str(e)}")


def _find_directive_by_name(directives: List[Directive], name: str) -> Optional[Directive]:
    """Find a directive in a list by its name (first argument)."""
    for directive in directives:
        if directive.arguments and directive.arguments[0].value == name:
            return directive
    return None


def _get_arg_value(directive: Directive, arg_name: str) -> Optional[str]:
    """Get the value of an argument by name from a directive."""
    for i, arg in enumerate(directive.arguments):
        if arg.value == arg_name and i + 1 < len(directive.arguments):
            return directive.arguments[i + 1].value
    return None


def _get_property_args(directive: Directive) -> Dict[str, str]:
    """Extract property name-value pairs from a directive's arguments."""
    result: Dict[str, str] = {}
    if len(directive.arguments) < 2:
        return result

    i = 0
    # Skip the first argument which is the directive name
    i += 1

    while i < len(directive.arguments) - 1:
        key = directive.arguments[i].value
        value = directive.arguments[i + 1].value
        result[key] = value
        i += 2

    return result


@overload
def confetti(cls: Type[T]) -> Type[T]: ...


@overload
def confetti(*, name: Optional[str] = None) -> Callable[[Type[T]], Type[T]]: ...


def confetti(cls: Optional[Type[T]] = None, *, name: Optional[str] = None) -> Union[Type[T], Callable[[Type[T]], Type[T]]]:
    """
    Decorator to mark a class as mappable to/from Confetti configuration.

    Args:
        cls: The class being decorated
        name: Optional custom name for the class in Confetti (defaults to class name)

    Returns:
        The decorated class
    """

    def decorator(cls: Type[T]) -> Type[T]:
        confetti_name = name or cls.__name__.lower()
        _CONFETTI_CLASSES[confetti_name] = cls

        # Add metadata to the class
        setattr(cls, "_confetti_name", confetti_name)

        # Make it a dataclass if it's not already
        if not is_dataclass(cls):
            cls = dataclasses.dataclass(cls)  # type: ignore

        return cls

    # Handle being called with or without arguments
    if cls is None:
        return decorator
    return decorator(cls)


def load_confetti(config_text: str, target_class: Type[T]) -> T:
    """
    Load a Confetti configuration into a Python object.

    Args:
        config_text: The Confetti configuration text
        target_class: The class to instantiate

    Returns:
        An instance of the target_class populated from the configuration
    """
    # Check if the target class is registered
    class_name = getattr(target_class, "_confetti_name", target_class.__name__.lower())
    if class_name not in _CONFETTI_CLASSES:
        confetti(target_class)  # type: ignore

    # Parse the configuration
    unit = parse_confetti(config_text)

    # Find the top-level directive for the target class
    top_directive = _find_directive_by_name(unit.root.subdirectives, class_name)
    if not top_directive:
        raise MappingError(f"No directive found for class {target_class.__name__}")

    return _load_object_from_directive(top_directive, target_class)


def load_confetti_file(file_path: Union[str, Path], target_class: Type[T]) -> T:
    """
    Load a Confetti configuration file into a Python object.

    Args:
        file_path: Path to the Confetti configuration file
        target_class: The class to instantiate

    Returns:
        An instance of the target_class populated from the configuration file
    """
    path = Path(file_path) if isinstance(file_path, str) else file_path
    with open(path, "r", encoding="utf-8") as f:
        config_text = f.read()
    return load_confetti(config_text, target_class)


def _load_object_from_directive(directive: Directive, target_class: Type[T]) -> T:
    """
    Load a Python object from a Confetti directive.

    Args:
        directive: The Confetti directive containing the object data
        target_class: The class to instantiate

    Returns:
        An instance of the target_class populated from the directive
    """
    # Get the class's fields and their types
    fields: Dict[str, Any] = {}
    type_hints = get_type_hints(target_class)

    # Get any simple properties from the directive arguments
    prop_args = _get_property_args(directive)
    for name, value in prop_args.items():
        if name in type_hints:
            fields[name] = _convert_value(value, type_hints[name])

    # Process subdirectives for nested objects
    for subdirective in directive.subdirectives:
        if not subdirective.arguments:
            continue

        field_name = subdirective.arguments[0].value
        if field_name in type_hints:
            field_type = type_hints[field_name]

            # If it's a registered confetti class
            field_type_name = getattr(field_type, "_confetti_name", getattr(field_type, "__name__", str(field_type)).lower())
            if field_type_name in _CONFETTI_CLASSES:
                # Load nested object
                fields[field_name] = _load_object_from_directive(subdirective, field_type)
            else:
                # Handle as a property with multiple arguments
                prop_args = _get_property_args(subdirective)
                if prop_args and field_name not in fields:
                    try:
                        # Try to convert to the expected type
                        if is_dataclass(field_type):
                            # Create instance of the nested dataclass
                            field_instance = field_type(**prop_args)  # type: ignore
                            fields[field_name] = field_instance
                        else:
                            # Fallback: store as dict or try direct conversion
                            fields[field_name] = prop_args
                    except Exception as e:
                        raise MappingError(f"Error mapping field {field_name}: {str(e)}")

    # Create the instance with the collected fields
    try:
        return target_class(**fields)
    except TypeError as e:
        raise MappingError(f"Error creating {target_class.__name__} instance: {str(e)}")


def dump_confetti(obj: Any) -> str:
    """
    Convert a Python object to Confetti configuration text.

    Args:
        obj: The object to convert (should be a class decorated with @confetti_class)

    Returns:
        Confetti configuration text
    """
    # Check if the object's class is registered
    class_name = getattr(obj.__class__, "_confetti_name", obj.__class__.__name__.lower())
    if class_name not in _CONFETTI_CLASSES:
        confetti(obj.__class__)  # type: ignore

    # Create a directive for the object
    directive = _create_directive_from_object(obj)

    # Create a Confetti unit with the directive
    unit = ConfettiUnit()
    unit.root.subdirectives.append(directive)

    # Convert to string
    output = StringIO()
    from .pyconfetti import print_directive

    for directive in unit.root.subdirectives:
        print_directive(directive, output=output)
    return output.getvalue()


def dump_confetti_file(obj: Any, file_path: Union[str, Path]) -> None:
    """
    Convert a Python object to Confetti configuration and write to a file.

    Args:
        obj: The object to convert (should be a class decorated with @confetti_class)
        file_path: Path where to write the configuration
    """
    config_text = dump_confetti(obj)
    path = Path(file_path) if isinstance(file_path, str) else file_path
    with open(path, "w", encoding="utf-8") as f:
        f.write(config_text)


def _create_directive_from_object(obj: Any) -> Directive:
    """
    Create a Confetti directive from a Python object.

    Args:
        obj: The object to convert

    Returns:
        A Confetti directive representing the object
    """
    directive = Directive()

    # Add the class name as the first argument
    class_name = getattr(obj.__class__, "_confetti_name", obj.__class__.__name__.lower())
    directive.arguments.append(Argument(value=class_name, offset=0, length=len(class_name)))

    # Get all fields
    fields: Dict[str, Any] = {}
    if is_dataclass(obj):
        fields = {f.name: getattr(obj, f.name) for f in dataclasses.fields(obj) if hasattr(obj, f.name)}
    else:
        # For non-dataclasses, get all public attributes
        fields = {name: value for name, value in obj.__dict__.items() if not name.startswith("_")}

    for name, value in fields.items():
        if value is None:
            continue

        # Check if it's a nested confetti class
        value_class = value.__class__
        value_class_name = getattr(value_class, "_confetti_name", value_class.__name__.lower())

        if value_class_name in _CONFETTI_CLASSES or is_dataclass(value):
            # Create a subdirective for the nested object
            subdirective = _create_directive_from_object(value)
            if subdirective.arguments:
                # Replace the class name with the field name
                subdirective.arguments[0].value = name
                subdirective.arguments[0].length = len(name)
                directive.subdirectives.append(subdirective)
        else:
            # Add as a simple property
            directive.arguments.append(Argument(value=name, offset=0, length=len(name)))
            value_str = str(value)
            directive.arguments.append(Argument(value=value_str, offset=0, length=len(value_str)))

    return directive


# Add to package exports
__all__ = [
    "confetti",
    "load_confetti",
    "load_confetti_file",
    "dump_confetti",
    "dump_confetti_file",
    "MappingError",
]
