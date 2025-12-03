from midnight.core.base import Node


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
