"""
High-level chain building APIs for intuitive workflow creation.

This module provides user-friendly ways to create node chains without
requiring knowledge of doubly linked list structures.
"""

from collections.abc import Callable

from twpm.core.base import Node
from twpm.core.cursor import Cursor


class Chain:
    """
    Unified API for creating workflows with multiple usage patterns.

    Can be used in three ways:

    1. Constructor with nodes (simplest):
        ```python
        workflow = Chain(node1, node2, node3).build()
        ```

    2. Builder pattern (flexible):
        ```python
        workflow = (Chain()
            .add(welcome_node)
            .add_if(is_premium, premium_node)
            .add_section([node1, node2, node3])
            .with_progress(fields=[...], after_each=QuestionNode)
            .build()
        )
        ```

    3. Using convenience function:
        ```python
        workflow = chain(node1, node2, node3)  # Auto-builds
        ```
    """

    def __init__(self, *nodes: Node):
        """
        Initialize a Chain with optional initial nodes.

        Args:
            *nodes: Optional nodes to initialize the chain with

        Example:
            ```python
            # Empty chain for builder pattern
            c = Chain()

            # Chain with initial nodes
            c = Chain(node1, node2, node3)
            ```
        """
        self._nodes: list[Node] = list(nodes)
        self._progress_config: dict | None = None

    def add(self, node: Node) -> "Chain":
        """
        Add a single node to the chain.

        Args:
            node: The node to add

        Returns:
            Self for method chaining

        Example:
            ```python
            builder.add(DisplayMessageNode("Hello"))
            ```
        """
        self._nodes.append(node)
        return self

    def add_section(self, nodes: list[Node]) -> "Chain":
        """
        Add multiple nodes at once.

        Args:
            nodes: List of nodes to add in sequence

        Returns:
            Self for method chaining

        Example:
            ```python
            builder.add_section([node1, node2, node3])
            ```
        """
        self._nodes.extend(nodes)
        return self

    def add_if(self, condition: bool, node: Node) -> "Chain":
        """
        Conditionally add a node based on a boolean condition.

        This is useful for feature flags, A/B testing, or environment-specific nodes.

        Args:
            condition: Whether to add the node
            node: The node to add if condition is True

        Returns:
            Self for method chaining

        Example:
            ```python
            builder.add_if(config.enable_premium, premium_node)
            ```
        """
        if condition:
            self._nodes.append(node)
        return self

    def with_progress(
        self,
        fields: list[tuple[str, str]],
        after_each: type | tuple[type, ...] | Callable[[Node], bool] | None = None,
        node_factory: Callable[[Node], Node] | None = None,
    ) -> "Chain":
        """
        Configure automatic progress tracking injection.

        This will automatically insert progress nodes after specified node types
        when build() is called.

        Args:
            fields: List of (label, data_key) tuples for progress tracking
            after_each: Node type(s) to insert progress after, or a filter function.
                       If None, inserts after every node.
            node_factory: Optional custom factory to create progress nodes.
                         If None, uses default ProgressNode.

        Returns:
            Self for method chaining

        Example:
            ```python
            builder.with_progress(
                fields=[("Name", "name"), ("Email", "email")],
                after_each=(QuestionNode, PoolNode)
            )
            ```
        """
        self._progress_config = {
            "fields": fields,
            "after_each": after_each,
            "node_factory": node_factory,
        }
        return self

    def build(self) -> Node:
        """
        Build and return the final chain.

        Links all nodes together and applies any configured operations
        like progress tracking injection.

        Returns:
            The head node of the built chain

        Raises:
            ValueError: If no nodes have been added

        Example:
            ```python
            head = chain.build()
            orchestrator.start(head)
            ```
        """
        if not self._nodes:
            raise ValueError("Cannot build empty chain. Add at least one node.")

        # Link all nodes together
        head = self._link_nodes()

        # Apply progress tracking if configured
        if self._progress_config:
            self._apply_progress_tracking(head)

        return head

    def _link_nodes(self) -> Node:
        """
        Link all nodes in the chain together.

        Returns:
            The head node of the linked chain
        """
        if len(self._nodes) == 1:
            return self._nodes[0]

        # Link nodes together
        for i in range(len(self._nodes) - 1):
            current = self._nodes[i]
            next_node = self._nodes[i + 1]

            current.next = next_node
            next_node.previous = current

        return self._nodes[0]

    def _apply_progress_tracking(self, head: Node) -> None:
        """
        Apply automatic progress tracking to the chain.

        Args:
            head: The head node of the chain
        """
        config = self._progress_config
        fields = config["fields"]
        after_each = config["after_each"]
        custom_factory = config["node_factory"]

        # Import here to avoid circular dependency
        from twpm.core.primitives.task import TaskNode

        # Determine filter function
        if after_each is None:
            filter_fn = None
        elif isinstance(after_each, type):

            def filter_fn(n):
                return isinstance(n, after_each)
        elif isinstance(after_each, tuple):

            def filter_fn(n):
                return isinstance(n, after_each)
        elif callable(after_each):
            filter_fn = after_each
        else:
            filter_fn = None

        # Create node factory
        if custom_factory:
            node_factory = custom_factory
        else:
            # Try to import ProgressNode, fallback to basic implementation
            try:
                from examples.cli.nodes import ProgressNode

                counter = [0]

                def node_factory(node: Node) -> Node:
                    counter[0] += 1
                    return ProgressNode(
                        fields=fields, title=None, key=f"progress_{counter[0]}"
                    )

            except ImportError:
                # If ProgressNode not available, create a simple display node
                def node_factory(node: Node) -> Node:
                    async def display_progress(data):
                        return True

                    return TaskNode(display_progress)

        # Find the last node in the chain
        last_node = head
        while last_node.next is not None:
            last_node = last_node.next

        # Apply progress tracking
        Cursor.add_after_each(
            begin=head, end=last_node, node_factory=node_factory, filter_fn=filter_fn
        )


def chain(*nodes: Node) -> Node:
    """
    Convenience function to quickly chain nodes together.

    This is syntactic sugar for `Chain(*nodes).build()`.
    Use this for simple, linear workflows where you don't need
    builder features like conditionals or progress tracking.

    Args:
        *nodes: Variable number of nodes to chain together in sequence

    Returns:
        The first node in the chain (head node)

    Raises:
        ValueError: If no nodes are provided

    Example:
        ```python
        # Simple one-liner
        workflow = chain(
            DisplayMessageNode("Welcome"),
            QuestionNode("Name", "name"),
            QuestionNode("Email", "email"),
            SummaryNode(fields=[...])
        )

        orchestrator.start(workflow)
        ```
    """
    return Chain(*nodes).build()
