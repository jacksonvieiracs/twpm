"""
Data models for the workflow system.

This module contains all data classes and models used for passing information
between nodes and managing workflow state.
"""

from dataclasses import dataclass

from twpm.core.base.types import NodeKey, Value


@dataclass
class NodeResult:
    """
    Result of a node execution.

    Contains information about whether the execution was successful,
    any data produced by the node, and status information.

    Attributes:
        success: Whether the node executed successfully
        data: Dictionary of data produced by the node execution
        message: Optional message providing context about the execution
        is_awaiting_input: Whether the node is waiting for external input
    """

    success: bool
    data: dict[str, str]
    message: str
    is_awaiting_input: bool = False


@dataclass
class ListData:
    """
    Shared data container passed between nodes during workflow execution.

    Provides dictionary-like access to workflow data with convenience methods
    for checking, getting, and updating values.

    Attributes:
        data: The underlying dictionary storing workflow data
    """

    data: dict[NodeKey, Value]

    def __getitem__(self, key: NodeKey) -> Value:
        """Get a value by key using bracket notation."""
        return self.data[key]

    def __setitem__(self, key: NodeKey, value: Value) -> None:
        """Set a value by key using bracket notation."""
        self.data[key] = value

    def get(self, key: NodeKey, default: Value | None = None):
        """
        Get a value by key with optional default.

        Args:
            key: The key to look up
            default: Value to return if key doesn't exist

        Returns:
            The value if found, otherwise the default
        """
        return self.data.get(key, default)

    def update(self, new_data: dict[NodeKey, Value]) -> None:
        """
        Update the data dictionary with new values.

        Args:
            new_data: Dictionary of key-value pairs to merge into the data
        """
        self.data.update(new_data)

    def has(self, key: NodeKey) -> bool:
        """
        Check if a key exists in the data.

        Args:
            key: The key to check for

        Returns:
            True if the key exists, False otherwise
        """
        return key in self.data
