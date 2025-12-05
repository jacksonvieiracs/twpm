"""
Node abstract base class.

This module defines the core Node interface that all workflow nodes must implement.
The Node class provides the basic structure for nodes in a linked list-based workflow.
"""

from abc import ABC, abstractmethod

from twpm.core.base.enums import NodeStatus
from twpm.core.base.models import ListData, NodeResult
from twpm.core.base.types import NodeKey


class Node(ABC):
    """
    Abstract base class for all workflow nodes.

    Nodes are the fundamental building blocks of workflows, forming a linked
    list structure where each node can execute some logic and pass data to
    the next node.

    Attributes:
        key: Unique identifier for this node
        next: Reference to the next node in the workflow
        previous: Reference to the previous node in the workflow
        status: Current execution status of the node
    """

    def __init__(self) -> None:
        """Initialize a new node with default values."""
        self.key: NodeKey
        self.next: Node | None = None
        self.previous: Node | None = None
        self.status: NodeStatus = NodeStatus.DEFAULT

    @abstractmethod
    async def execute(self, data: ListData) -> NodeResult:
        """
        Execute the node's logic.

        This method must be implemented by all concrete node classes.
        It receives shared workflow data and returns a result indicating
        success/failure and any data produced.

        Args:
            data: Shared workflow data accessible to all nodes

        Returns:
            NodeResult containing execution status and any produced data
        """
        ...
