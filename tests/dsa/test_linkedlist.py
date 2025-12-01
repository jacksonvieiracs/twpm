from midnight.dsa.linkedlist import LinkedList, Node


class TestLinkedList:
    def test_get_existent_element(self):
        linked_list = LinkedList()
        linked_list.append(10)
        linked_list.append(15)
        assert linked_list[0].element == 10

    def test_pop_at_head_position(self):
        linked_list = LinkedList()

        assert len(linked_list) == 0
        linked_list.insert(0, 10)

        assert len(linked_list) == 1
        linked_list.pop(0)

        assert len(linked_list) == 0

    def test_pop_last_element(self):
        linked_list = LinkedList()

        assert len(linked_list) == 0

        linked_list.append(10)
        linked_list.append(30)
        linked_list.append(20)

        assert len(linked_list) == 3
        linked_list.pop(2)

        assert len(linked_list) == 2
        assert linked_list[1].element == 30

    def test_insert_at_head_position(self):
        linked_list = LinkedList()

        assert len(linked_list) == 0
        linked_list.insert(0, 10)

        assert len(linked_list) == 1
        assert linked_list[0].element == 10

    def test_set_at_head_position(self):
        linked_list = LinkedList()
        linked_list.append(10)
        linked_list.append(20)

        assert len(linked_list) == 2
        linked_list[0] = Node(element=30)

        assert linked_list[0].element == 30
        assert linked_list[1].element == 20
        assert len(linked_list) == 2

    def test_is_empty_linkedlist_bool(self):
        linked_list = LinkedList()
        assert not linked_list

        linked_list.append(20)
        assert linked_list

    def test_clear_should_reset_head(self):
        linked_list = LinkedList()
        linked_list.append(20)

        assert len(linked_list) == 1
        linked_list.clear()

        assert len(linked_list) == 0
        assert linked_list.head == None
