from .interfaces.node import Node


class Cursor:
    @staticmethod
    def insert(target: Node, new_node: Node) -> None:
        target_next = target.next
        target.next = new_node
        new_node.next = target_next
