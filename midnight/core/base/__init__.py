"""
Core interfaces for the workflow system.

This module re-exports all public interfaces, types, and models for easy importing.
Users can import everything they need from midnight.core.interfaces instead of
needing to know the internal module structure.

Example:
    >>> from midnight.core.interfaces import Node, NodeResult, NodeStatus, ListData
"""

from midnight.core.base.enums import NodeStatus
from midnight.core.base.models import ListData, NodeResult
from midnight.core.base.node import Node
from midnight.core.base.types import NodeKey, Value

__all__ = [
    # Types
    "NodeKey",
    "Value",
    # Enums
    "NodeStatus",
    # Models
    "NodeResult",
    "ListData",
    # Base classes
    "Node",
]
