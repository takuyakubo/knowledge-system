"""Utility helper functions."""

import json
from pathlib import Path
from typing import TypeVar

from knowledge_system.types import JSONObject, JSONValue

T = TypeVar("T")


def load_json_file(filepath: str | Path) -> JSONObject:
    """Load JSON data from a file.

    Parameters
    ----------
    filepath : str | Path
        Path to JSON file

    Returns
    -------
    JSONObject
        Loaded JSON data as a dictionary

    Raises
    ------
    FileNotFoundError
        If file doesn't exist
    ValueError
        If file contains invalid JSON
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            result = json.load(f)
            # json.load returns Any, but we expect dict[str, Any]
            if not isinstance(result, dict):
                type_name = type(result).__name__
                raise ValueError(f"Expected JSON object in {path}, got {type_name}")
            return result
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e


def save_json_file(
    data: JSONObject,
    filepath: str | Path,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Save data to a JSON file.

    Parameters
    ----------
    data : JSONObject
        JSON-compatible dictionary to save
    filepath : str | Path
        Path to save to
    indent : int
        JSON indentation level
    ensure_ascii : bool
        Whether to escape non-ASCII characters
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def chunk_list(items: list[T], chunk_size: int) -> list[list[T]]:
    """Split a list into chunks of specified size.

    Parameters
    ----------
    items : list[T]
        Items to chunk
    chunk_size : int
        Size of each chunk

    Returns
    -------
    list[list[T]]
        List of chunks

    Raises
    ------
    ValueError
        If chunk_size is not positive

    Examples
    --------
    >>> chunk_list([1, 2, 3, 4, 5], 2)
    [[1, 2], [3, 4], [5]]
    """
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")

    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def flatten_dict(
    nested_dict: dict[str, JSONValue],
    *,
    separator: str = ".",
    prefix: str = "",
) -> dict[str, JSONValue]:
    """Flatten a nested dictionary.

    Parameters
    ----------
    nested_dict : dict[str, JSONValue]
        Dictionary with JSON-compatible values to flatten
    separator : str
        Separator for keys
    prefix : str
        Prefix for all keys

    Returns
    -------
    dict[str, JSONValue]
        Flattened dictionary with dot-notation keys

    Examples
    --------
    >>> flatten_dict({"a": {"b": 1, "c": 2}})
    {"a.b": 1, "a.c": 2}
    """
    items: list[tuple[str, JSONValue]] = []

    for key, value in nested_dict.items():
        new_key = f"{prefix}{separator}{key}" if prefix else key

        if isinstance(value, dict):
            items.extend(
                flatten_dict(value, separator=separator, prefix=new_key).items()
            )
        else:
            items.append((new_key, value))

    return dict(items)
