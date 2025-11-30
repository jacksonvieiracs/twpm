import pytest

from midnight.dsa import linkedlist
from midnight.dsa.linkedlist import LinkedList


class TestLinkedList:
    def test_get_existent_element(self):
        linked_list = LinkedList()
        linked_list.push(10)
        linked_list.push(15)

        assert linked_list.get(1) == 10

    def test_get_out_of_range_index(self):
        linked_list = LinkedList()
        linked_list.push(5)
        linked_list.push(15)
        pytest.raises(IndexError, linked_list.get, 3)

    def test_insert_with_empty_list_should_grow_with_default_values(self):
        linked_list = LinkedList()

        assert linked_list.size == 0
        linked_list.insert(5, 10)

        assert linked_list.size == 6
        assert linked_list.get(5) == 10
