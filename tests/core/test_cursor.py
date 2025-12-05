import pytest

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.cursor import Cursor


class DummyNode(Node):
    """A simple test node for testing cursor operations."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.key = name

    async def execute(self, data: ListData) -> NodeResult:
        return NodeResult(
            success=True,
            data={},
            message=f"{self.name} executed",
            is_awaiting_input=False,
        )

    def __repr__(self):
        return f"DummyNode({self.name})"


class TypeANode(Node):
    """Test node of type A."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.key = name

    async def execute(self, data: ListData) -> NodeResult:
        return NodeResult(
            success=True, data={}, message=f"TypeA {self.name}", is_awaiting_input=False
        )

    def __repr__(self):
        return f"TypeANode({self.name})"


class TypeBNode(Node):
    """Test node of type B."""

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.key = name

    async def execute(self, data: ListData) -> NodeResult:
        return NodeResult(
            success=True, data={}, message=f"TypeB {self.name}", is_awaiting_input=False
        )

    def __repr__(self):
        return f"TypeBNode({self.name})"


@pytest.mark.asyncio
class TestCursor:
    """Test suite for Cursor operations."""

    async def test_insert_single_node(self):
        """Test inserting a single node between two nodes."""
        node_a = DummyNode("A")
        node_b = DummyNode("B")
        node_c = DummyNode("C")

        # Create chain: A -> C
        node_a.next = node_c
        node_c.previous = node_a

        # Insert B between A and C
        Cursor.insert(node_a, node_b)

        # Verify chain: A -> B -> C
        assert node_a.next is node_b
        assert node_b.next is node_c

    async def test_insert_single_node_at_end(self):
        """Test inserting a node at the end of the chain."""
        node_a = DummyNode("A")
        node_b = DummyNode("B")

        # A has no next
        assert node_a.next is None

        # Insert B after A
        Cursor.insert(node_a, node_b)

        # Verify: A -> B
        assert node_a.next is node_b
        assert node_b.next is None

    async def test_get_range_full_chain(self):
        """Test getting all nodes from begin to end."""
        node_a = DummyNode("A")
        node_b = DummyNode("B")
        node_c = DummyNode("C")
        node_d = DummyNode("D")

        # Create chain: A -> B -> C -> D
        node_a.next = node_b
        node_b.previous = node_a
        node_b.next = node_c
        node_c.previous = node_b
        node_c.next = node_d
        node_d.previous = node_c

        nodes = Cursor.get_range(node_a, node_d)

        assert len(nodes) == 4
        assert nodes[0] is node_a
        assert nodes[1] is node_b
        assert nodes[2] is node_c
        assert nodes[3] is node_d

    async def test_get_range_single_node(self):
        """Test getting range where begin equals end."""
        node_a = DummyNode("A")
        node_b = DummyNode("B")

        node_a.next = node_b
        node_b.previous = node_a

        nodes = Cursor.get_range(node_a, node_a)

        assert len(nodes) == 1
        assert nodes[0] is node_a

    async def test_get_range_partial_chain(self):
        """Test getting a subset of nodes from a chain."""
        node_a = DummyNode("A")
        node_b = DummyNode("B")
        node_c = DummyNode("C")
        node_d = DummyNode("D")

        # Create chain: A -> B -> C -> D
        node_a.next = node_b
        node_b.previous = node_a
        node_b.next = node_c
        node_c.previous = node_b
        node_c.next = node_d
        node_d.previous = node_c

        nodes = Cursor.get_range(node_b, node_c)

        assert len(nodes) == 2
        assert nodes[0] is node_b
        assert nodes[1] is node_c

    async def test_find_by_type_mixed_types(self):
        """Test finding nodes of specific type in mixed chain."""
        node_a = TypeANode("A1")
        node_b = TypeBNode("B1")
        node_c = TypeANode("A2")
        node_d = TypeBNode("B2")

        # Create chain: A -> B -> A -> B
        node_a.next = node_b
        node_b.previous = node_a
        node_b.next = node_c
        node_c.previous = node_b
        node_c.next = node_d
        node_d.previous = node_c

        type_a_nodes = Cursor.find_by_type(node_a, node_d, TypeANode)
        type_b_nodes = Cursor.find_by_type(node_a, node_d, TypeBNode)

        assert len(type_a_nodes) == 2
        assert type_a_nodes[0] is node_a
        assert type_a_nodes[1] is node_c

        assert len(type_b_nodes) == 2
        assert type_b_nodes[0] is node_b
        assert type_b_nodes[1] is node_d

    async def test_find_by_type_no_matches(self):
        """Test finding nodes when no nodes match the type."""
        node_a = TypeANode("A1")
        node_b = TypeANode("A2")

        node_a.next = node_b
        node_b.previous = node_a

        type_b_nodes = Cursor.find_by_type(node_a, node_b, TypeBNode)

        assert len(type_b_nodes) == 0

    async def test_find_by_type_all_match(self):
        """Test finding nodes when all nodes match the type."""
        node_a = TypeANode("A1")
        node_b = TypeANode("A2")
        node_c = TypeANode("A3")

        node_a.next = node_b
        node_b.previous = node_a
        node_b.next = node_c
        node_c.previous = node_b

        type_a_nodes = Cursor.find_by_type(node_a, node_c, TypeANode)

        assert len(type_a_nodes) == 3
        assert type_a_nodes[0] is node_a
        assert type_a_nodes[1] is node_b
        assert type_a_nodes[2] is node_c

    async def test_add_after_each_with_filter(self):
        """Test adding nodes after each node matching the filter."""
        node_a = TypeANode("A1")
        node_b = TypeBNode("B1")
        node_c = TypeANode("A2")
        node_d = TypeBNode("B2")

        # Create chain: A -> B -> A -> B
        node_a.next = node_b
        node_b.previous = node_a
        node_b.next = node_c
        node_c.previous = node_b
        node_c.next = node_d
        node_d.previous = node_c

        # Add DummyNode after each TypeANode
        counter = [0]

        def node_factory(node):
            counter[0] += 1
            return DummyNode(f"X{counter[0]}")

        Cursor.add_after_each(
            begin=node_a,
            end=node_d,
            node_factory=node_factory,
            filter_fn=lambda n: isinstance(n, TypeANode),
        )

        # Expected chain: A1 -> X1 -> B1 -> A2 -> X2 -> B2
        assert node_a.next.name == "X1"
        assert node_a.next.next is node_b
        assert node_b.next is node_c
        assert node_c.next.name == "X2"
        assert node_c.next.next is node_d
        assert node_d.next is None

        # Verify backwards links
        assert node_b.previous.name == "X1"
        assert node_b.previous.previous is node_a
        assert node_d.previous.name == "X2"
        assert node_d.previous.previous is node_c

    async def test_add_after_each_no_filter(self):
        """Test adding nodes after every node when no filter is provided."""
        node_a = DummyNode("A")
        node_b = DummyNode("B")
        node_c = DummyNode("C")

        # Create chain: A -> B -> C
        node_a.next = node_b
        node_b.previous = node_a
        node_b.next = node_c
        node_c.previous = node_b

        counter = [0]

        def node_factory(node):
            counter[0] += 1
            return DummyNode(f"X{counter[0]}")

        # Add after each node (no filter)
        Cursor.add_after_each(
            begin=node_a, end=node_c, node_factory=node_factory, filter_fn=None
        )

        # Expected chain: A -> X1 -> B -> X2 -> C -> X3
        assert node_a.next.name == "X1"
        assert node_a.next.next is node_b
        assert node_b.next.name == "X2"
        assert node_b.next.next is node_c
        assert node_c.next.name == "X3"

    async def test_add_after_each_filter_no_matches(self):
        """Test adding nodes when filter matches no nodes."""
        node_a = TypeANode("A1")
        node_b = TypeANode("A2")

        node_a.next = node_b
        node_b.previous = node_a

        counter = [0]

        def node_factory(node):
            counter[0] += 1
            return DummyNode(f"X{counter[0]}")

        # Filter for TypeBNode (none exist)
        Cursor.add_after_each(
            begin=node_a,
            end=node_b,
            node_factory=node_factory,
            filter_fn=lambda n: isinstance(n, TypeBNode),
        )

        # Chain should remain unchanged: A1 -> A2
        assert node_a.next is node_b
        assert node_b.previous is node_a
        assert node_b.next is None
        assert counter[0] == 0  # No nodes were created

    async def test_add_after_each_single_node(self):
        """Test adding after a single node range."""
        node_a = TypeANode("A1")

        counter = [0]

        def node_factory(node):
            counter[0] += 1
            return DummyNode(f"X{counter[0]}")

        Cursor.add_after_each(
            begin=node_a,
            end=node_a,
            node_factory=node_factory,
            filter_fn=lambda n: isinstance(n, TypeANode),
        )

        # Expected chain: A1 -> X1
        assert node_a.next.name == "X1"
        assert node_a.next.next is None

    async def test_add_after_each_maintains_chain_integrity(self):
        """Test that add_after_each maintains full chain integrity."""
        node_a = DummyNode("A")
        node_b = DummyNode("B")
        node_c = DummyNode("C")

        # Create chain: A -> B -> C
        node_a.next = node_b
        node_b.previous = node_a
        node_b.next = node_c
        node_c.previous = node_b

        Cursor.add_after_each(
            begin=node_a,
            end=node_c,
            node_factory=lambda n: DummyNode(f"X-after-{n.name}"),
            filter_fn=None,
        )

        # Walk the chain forward and verify integrity
        current = node_a
        nodes_forward = []
        while current is not None:
            nodes_forward.append(current.name)
            if current.next:
                assert current.next.previous is current
            current = current.next

        # Expected: A, X-after-A, B, X-after-B, C, X-after-C
        assert len(nodes_forward) == 6
        assert nodes_forward == ["A", "X-after-A", "B", "X-after-B", "C", "X-after-C"]

        # Walk the chain backward and verify
        current = node_a
        while current.next is not None:
            current = current.next

        nodes_backward = []
        while current is not None:
            nodes_backward.append(current.name)
            if current.previous:
                assert current.previous.next is current
            current = current.previous

        nodes_backward.reverse()
        assert nodes_backward == nodes_forward
