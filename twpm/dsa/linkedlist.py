from dataclasses import dataclass
from typing import Self


@dataclass
class Node:
    element: int = 0
    next: "Node | None" = None


class LinkedList:
    def __init__(self):
        self._count = 0
        self._head: Node | None = None

    def append(self, element: int):
        node = Node(element=element)
        if self._count == 0:
            self._head = node
        else:
            last = self[self._count - 1]
            last.next = node
        self._count += 1

    def pop(self, index: int) -> Node:
        abs_index = abs(index)

        if abs_index >= self._count and index != 0:
            raise IndexError("Index out of range")

        current = self._head

        if abs_index == 0:
            self._head = current.next
        else:
            previous = self[abs_index - 1]
            current = previous.next
            previous.next = current.next

        self._count -= 1

        return current

    def insert(self, index: int, element: int):
        abs_index = abs(index)

        if abs_index >= self._count and index != 0:
            raise IndexError("Index out of range")

        node = Node(element=element)

        if abs_index == 0:
            current = self._head
            node.next = current
            self._head = node
        else:
            previous = self[abs_index - 1]
            current = previous.next
            previous.next = node
            node.next = current

        self._count += 1

    def extend(self, list: Self):
        if len(list) == 0:
            return

        last = self[self._count - 1]
        first = list[0]

        last.next = first
        self._count += len(list)

    def insert_after(self, index: int, element: int):
        abs_index = abs(index)

        if abs_index >= self._count:
            raise IndexError("Index out of range")

        node = Node(element=element)
        current = self[abs_index]
        current_next = current.next

        current.next = node
        node.next = current_next

        self._count += 1

    def clear(self):
        self._head = None
        self._count = 0

    def get_head(self) -> Node | None:
        return self._head

    def __bool__(self):
        return self._count > 0

    def __len__(self):
        return self._count

    def __setitem__(self, index: int, node: Node):
        "replace the item in the index with the given node"
        abs_index = abs(index)
        if abs_index >= self._count and index != 0:
            raise IndexError("Index out of range")

        current = self._head

        if abs_index == 0:
            node.next = current.next
            self._head = node
        else:
            previous = self[abs_index - 1]
            current = previous.next
            node.next = current.next
            previous.next = node

    def __getitem__(self, index: int) -> Node:
        abs_index = abs(index)

        if abs_index >= self._count and index != 0:
            raise IndexError("Index out of range")

        node = self._head

        for _ in range(index):
            node = node.next

        return node

    def __str__(self):
        current = self._head
        elements = []
        while current:
            elements.append(str(current.element))
            current = current.next
        return " -> ".join(elements)
