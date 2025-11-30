from dataclasses import dataclass
from typing import Self


@dataclass
class Node:
    element: int = 0
    next: Self | None = None


class LinkedList:
    def __init__(self):
        self.count = 0
        self.head: Node | None = None

    def __len__(self):
        return self.count

    def __getitem__(self, index: int) -> int | None:
        if index < 0 or index >= self.count:
            raise IndexError("Index out of range")

        interations = index
        current = self.head

        while interations > 0 and current:
            current = current.next
            interations -= 1

        if current is None:
            return None

        return current.element

    def __bool__(self):
        return self.count > 0

    def push(self, element: int):
        node = Node(element=element)
        if self.head is None:
            self.head = node
        else:
            head = self.head
            node.next = head
            self.head = node

        self.count += 1

    def insert(self, index: int, element: int):
        if index < 0:
            raise ValueError("Index cannot be negative")

        interations = index - 1

        current = self.head
        if current is None:
            self.head = Node()
            current = self.head
            self.count += 1

        while interations > 0:
            if current.next is None:
                node = Node()
                current.next = node
                self.count += 1

            current = current.next
            interations -= 1

        node = Node(element=element)
        assert current is not None
        current.next = node
        self.count += 1

    def __str__(self):
        current = self.head
        elements = []
        while current:
            elements.append(str(current.element))
            current = current.next
        return " -> ".join(elements)
