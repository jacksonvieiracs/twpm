import pytest

from midnight.dsa import linkedlist
from midnight.dsa.linkedlist import LinkedList


class TestLinkedList:
    def test_get_existent_element(self):
        linked_list = LinkedList()
        linked_list.push(10)
        linked_list.push(15)
        assert linked_list[1] == 10

    # def test_get_out_of_range_index(self):
    #     linked_list = LinkedList()
    #     linked_list.push(5)
    #     linked_list.push(15)
    # pytest.raises(IndexError, linked_list)

    def test_insert_with_empty_list_should_grow_with_default_values(self):
        linked_list = LinkedList()

        assert len(linked_list) == 0
        linked_list.insert(5, 10)

        assert len(linked_list) == 6
        assert linked_list[5] == 10

    def test_is_empty_linkedlist_bool(self):
        linked_list = LinkedList()
        assert not linked_list

        linked_list.push(20)
        assert linked_list
