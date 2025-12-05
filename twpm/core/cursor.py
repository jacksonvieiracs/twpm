from collections.abc import Callable

from twpm.core.base import Node


class Cursor:
    @staticmethod
    def insert(target: Node, new_node: Node) -> None:
        """
        The new node is a part of linked list, this method should interate in the new_node and get
        the end, and connect with the target
        target             target_next
            []<->       <->[]
                 []<->[]
           new_node   new_node_end
        """
        target_next = target.next
        target.next = new_node
        new_node.next = target_next

    @staticmethod
    def get_range(begin: Node, end: Node) -> list[Node]:
        """
        Collect all nodes from begin to end (inclusive) into a list.

        Args:
            begin: The starting node of the range
            end: The ending node of the range (inclusive)

        Returns:
            List of nodes from begin to end in order

        Example:
            nodes = Cursor.get_range(node_a, node_c)
            # Returns [node_a, node_b, node_c]
        """
        nodes = []
        current = begin

        while current is not None:
            nodes.append(current)
            if current is end:
                break
            current = current.next

        return nodes

    @staticmethod
    def find_by_type(begin: Node, end: Node, node_type: type) -> list[Node]:
        """
        Find all nodes of a specific type between begin and end (inclusive).

        Args:
            begin: The starting node of the range
            end: The ending node of the range (inclusive)
            node_type: The type of node to search for

        Returns:
            List of nodes matching the specified type

        Example:
            questions = Cursor.find_by_type(start, end, QuestionNode)
            # Returns all QuestionNode instances in the range
        """
        nodes = Cursor.get_range(begin, end)
        return [node for node in nodes if isinstance(node, node_type)]

    @staticmethod
    def add_after_each(
        begin: Node,
        end: Node,
        node_factory: Callable[[Node], Node],
        filter_fn: Callable[[Node], bool] | None = None,
    ) -> None:
        """
        Insert a new node after each node matching the filter function.

        Iterates from begin to end, and after each node where filter_fn returns True,
        inserts a new node created by node_factory(current_node). If filter_fn is None,
        adds a node after every node in the range.

        Args:
            begin: The starting node of the range
            end: The ending node of the range (inclusive)
            node_factory: Function that creates a new node, receives the current node
            filter_fn: Optional function to filter which nodes to add after.
                      If None, adds after every node.

        Example:
            # Add progress node after each question
            Cursor.add_after_each(
                begin=start_node,
                end=end_node,
                node_factory=lambda n: ProgressNode(fields=fields),
                filter_fn=lambda n: isinstance(n, QuestionNode)
            )
        """
        current = begin
        original_end = end

        while current is not None:
            should_add = filter_fn(current) if filter_fn else True
            is_end = current is original_end

            if should_add:
                new_node = node_factory(current)
                # Insert new_node after current
                next_node = current.next
                current.next = new_node
                new_node.previous = current
                new_node.next = next_node
                if next_node:
                    next_node.previous = new_node

                # Move to next_node (skip the newly inserted node)
                current = next_node
            else:
                current = current.next

            # Stop if we reached the original end node
            if is_end:
                break
