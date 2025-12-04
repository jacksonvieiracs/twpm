"""
Enumerations for the workflow system.

This module contains all enum types used in the node execution system,
providing type-safe status tracking and workflow state management.
"""

from enum import Enum


class NodeStatus(Enum):
    """
    Enumeration of possible node execution states.

    Attributes:
        DEFAULT: Node has not been executed or is ready to execute
        COMPLETE: Node executed successfully
        FAILED: Node execution failed
        AWAITING_INPUT: Node is paused waiting for external input
    """

    DEFAULT = "default"
    COMPLETE = "complete"
    FAILED = "failed"
    AWAITING_INPUT = "awaiting_input"
