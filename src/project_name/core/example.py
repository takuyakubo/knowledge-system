"""Example module demonstrating best practices."""

from dataclasses import dataclass
from typing import Any, Protocol

from project_name.types import ItemDict


class DataProcessor(Protocol):
    """Protocol for data processors."""

    def process(self, data: list[ItemDict]) -> list[ItemDict]:
        """Process a list of data items."""
        ...


@dataclass
class ExampleConfig:
    """Configuration for ExampleClass."""

    name: str
    max_items: int = 100
    enable_validation: bool = True

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.max_items <= 0:
            raise ValueError(f"max_items must be positive, got {self.max_items}")


class ExampleClass:
    """Example class demonstrating type hints and documentation.

    This class shows how to properly structure a Python class with:
    - Type hints for all methods
    - Comprehensive docstrings
    - Proper error handling

    Attributes
    ----------
    config : ExampleConfig
        Configuration for this instance
    data : list[dict[str, Any]]
        Internal data storage

    Examples
    --------
    >>> config = ExampleConfig(name="test", max_items=50)
    >>> example = ExampleClass(config)
    >>> example.add_item({"id": 1, "value": "test"})
    >>> len(example)
    1
    """

    def __init__(self, config: ExampleConfig) -> None:
        """Initialize ExampleClass with configuration.

        Parameters
        ----------
        config : ExampleConfig
            Configuration object
        """
        self.config = config
        self.data: list[ItemDict] = []

    def add_item(self, item: ItemDict) -> None:
        """Add an item to the internal storage.

        Parameters
        ----------
        item : dict[str, Any]
            Item to add

        Raises
        ------
        ValueError
            If max_items limit is reached or validation fails
        """
        if len(self.data) >= self.config.max_items:
            raise ValueError(
                f"Cannot add item: max_items limit ({self.config.max_items}) reached"
            )

        if self.config.enable_validation:
            self._validate_item(item)

        self.data.append(item)

    def _validate_item(self, item: ItemDict) -> None:
        """Validate an item before adding.

        Parameters
        ----------
        item : dict[str, Any]
            Item to validate

        Raises
        ------
        ValueError
            If item is invalid
        """
        # Type checking is handled by mypy, but runtime check for safety
        if not isinstance(item, dict):
            raise ValueError(f"Item must be a dictionary, got {type(item).__name__}")

        # Validate required fields
        required_fields = {"id", "name", "value"}
        missing_fields = required_fields - set(item.keys())
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")

        if not item:
            raise ValueError("Item cannot be empty")

    def get_items(
        self,
        *,
        filter_key: str | None = None,
        filter_value: Any | None = None,
    ) -> list[ItemDict]:
        """Get items with optional filtering.

        Parameters
        ----------
        filter_key : str | None
            Key to filter by
        filter_value : Any | None
            Value to filter by

        Returns
        -------
        list[dict[str, Any]]
            Filtered items
        """
        if filter_key is None or filter_value is None:
            return self.data.copy()

        return [item for item in self.data if item.get(filter_key) == filter_value]

    def __len__(self) -> int:
        """Return the number of items."""
        return len(self.data)

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"ExampleClass(name={self.config.name!r}, "
            f"items={len(self)}/{self.config.max_items})"
        )


def process_data(
    data: list[ItemDict],
    processor: DataProcessor,
    *,
    validate: bool = True,
) -> list[ItemDict]:
    """Process data using a processor.

    Parameters
    ----------
    data : list[dict[str, Any]]
        Data to process
    processor : DataProcessor
        Processor to use
    validate : bool
        Whether to validate data before processing

    Returns
    -------
    list[dict[str, Any]]
        Processed data

    Raises
    ------
    ValueError
        If validation fails
    """
    if validate and not data:
        raise ValueError("Data cannot be empty")

    return processor.process(data)
