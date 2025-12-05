"""
Core interfaces for the workflow system.

This module re-exports all public interfaces, types, and models for easy importing.
Users can import everything they need from twpm.core.interfaces instead of
needing to know the internal module structure.

Example:
    >>> from twpm.core.interfaces import Node, NodeResult, NodeStatus, ListData
"""

from twpm.core.base.enums import NodeStatus
from twpm.core.base.models import ListData, NodeResult
from twpm.core.base.node import Node
from twpm.core.base.types import NodeKey, Value

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
