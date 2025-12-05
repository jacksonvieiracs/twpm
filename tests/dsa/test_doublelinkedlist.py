import pytest

from twpm.dsa.doublelinkedlist import DoubleLinkedList


class TestDoubleLinkedList:
    def test_pop_at_head_position(self):
        """Test popping from head updates head, prev pointers, and tail if needed"""
        linked_list = DoubleLinkedList()

        assert len(linked_list) == 0
        linked_list.insert(0, 10)

        assert len(linked_list) == 1
        popped = linked_list.pop(0)

        assert len(linked_list) == 0
        assert popped.element == 10
        assert linked_list.get_head() is None
        assert linked_list.get_tail() is None

    def test_pop_last_element(self):
        """Test popping last element updates tail and prev pointers"""
        linked_list = DoubleLinkedList()

        assert len(linked_list) == 0

        linked_list.append(10)
        linked_list.append(30)
        linked_list.append(20)

        assert len(linked_list) == 3
        assert linked_list.get_tail().element == 20

        popped = linked_list.pop(2)

        assert len(linked_list) == 2
        assert linked_list[1].element == 30
        assert popped.element == 20
        assert linked_list.get_tail().element == 30
        assert linked_list.get_tail().next is None

    def test_insert_after_with_empty_list(self):
        """Should raise IndexError when inserting after in an empty list"""
        linked_list = DoubleLinkedList()
        with pytest.raises(IndexError):
            linked_list.insert_after(0, 10)

    def test_insert_after_in_middle_of_list(self):
        """Test insert_after updates both next and prev pointers correctly"""
        linked_list = DoubleLinkedList()
        linked_list.append(10)
        linked_list.append(20)
        linked_list.insert_after(0, 15)

        first = linked_list[0]
        middle = linked_list[1]
        last = linked_list[2]

        assert len(linked_list) == 3
        assert first.next.element == 15
        assert middle.element == 15
        assert middle.prev.element == 10
        assert middle.next.element == 20
        assert last.prev.element == 15

    def test_insert_after_in_the_end_of_list(self):
        """Test insert_after at end updates tail and prev pointers"""
        linked_list = DoubleLinkedList()
        linked_list.append(10)
        linked_list.append(20)

        cached_index = len(linked_list) - 1
        linked_list.insert_after(cached_index, 15)

        end = linked_list[cached_index]
        new_last = linked_list[2]

        assert end.next.element == 15
        assert new_last.element == 15
        assert new_last.prev.element == 20
        assert new_last.next is None
        assert linked_list.get_tail().element == 15

    def test_insert_at_head_position(self):
        """Test insert at head with existing elements updates prev pointers"""
        linked_list = DoubleLinkedList()

        assert len(linked_list) == 0
        linked_list.insert(0, 10)

        assert len(linked_list) == 1
        assert linked_list[0].element == 10
        assert linked_list.get_head().element == 10
        assert linked_list.get_tail().element == 10

    def test_insert_in_empty_list(self):
        """Test insert in empty list sets both head and tail"""
        linked_list = DoubleLinkedList()
        linked_list.insert(0, 15)

        assert len(linked_list) == 1
        assert linked_list.get_head().element == 15
        assert linked_list.get_tail().element == 15
        assert linked_list.get_head().prev is None
        assert linked_list.get_head().next is None

    def test_insert_in_middle_of_list(self):
        """Test insert in middle updates both next and prev pointers"""
        linked_list = DoubleLinkedList()
        linked_list.append(15)
        linked_list.append(50)
        linked_list.insert(1, 30)

        first = linked_list[0]
        middle = linked_list[1]
        last = linked_list[2]

        assert len(linked_list) == 3
        assert first.next.element == 30
        assert middle.element == 30
        assert middle.prev.element == 15
        assert middle.next.element == 50
        assert last.prev.element == 30
