from dataclasses import dataclass

from .linkedlist import LinkedList


@dataclass
class DoubleNode:
    element: int = 0
    prev: "DoubleNode | None" = None
    next: "DoubleNode | None" = None


class DoubleLinkedList(LinkedList):
    def __init__(self):
        super().__init__()
        # self._head: DoubleNode | None = None
        self._tail: DoubleNode | None = None

    def append(self, element: int):
        node = DoubleNode(element=element)

        if self._count == 0:
            self._head = node
            self._tail = node
        else:
            last = self[self._count - 1]
            last.next = node
            node.prev = last
            self._tail = node

        self._count += 1

    def pop(self, index: int) -> DoubleNode:
        abs_index = abs(index)

        if abs_index >= self._count and index != 0:
            raise IndexError("Index out of range")

        current = self._head

        if abs_index == 0:
            self._head = current.next
            if self._head:
                self._head.prev = None
            else:
                self._tail = None
        else:
            previous = self[abs_index - 1]
            current = previous.next
            previous.next = current.next
            if current.next:
                current.next.prev = previous
            else:
                self._tail = previous

        self._count -= 1

        return current

    def insert(self, index: int, element: int):
        abs_index = abs(index)

        if abs_index >= self._count and index != 0:
            raise IndexError("Index out of range")

        node = DoubleNode(element=element)

        if abs_index == 0:
            current = self._head
            node.next = current
            if current:
                current.prev = node
            self._head = node
            if self._count == 0:
                self._tail = node
        else:
            previous = self[abs_index - 1]
            current = previous.next
            previous.next = node
            node.prev = previous
            node.next = current
            if current:
                current.prev = node
            else:
                self._tail = node

        self._count += 1

    def insert_after(self, index: int, element: int):
        abs_index = abs(index)

        if abs_index >= self._count:
            raise IndexError("Index out of range")

        node = DoubleNode(element=element)
        current = self[abs_index]
        current_next = current.next

        current.next = node
        node.prev = current
        node.next = current_next
        if current_next:
            current_next.prev = node
        else:
            self._tail = node

        self._count += 1

    def get_tail(self):
        return self._tail
