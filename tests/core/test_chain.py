import pytest

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.chain import Chain, chain


class DummyNode(Node):
    """Simple test node."""

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


@pytest.mark.asyncio
class TestChainFunction:
    """Test suite for chain() function."""

    async def test_chains_two_nodes(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")

        # Act
        head = chain(node1, node2)

        # Assert
        assert head is node1
        assert node1.next is node2
        assert node2.previous is node1

    async def test_chains_three_nodes(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")
        node3 = DummyNode("C")

        # Act
        head = chain(node1, node2, node3)

        # Assert
        assert head is node1
        assert node1.next is node2
        assert node2.previous is node1
        assert node2.next is node3
        assert node3.previous is node2

    async def test_chains_many_nodes(self):
        # Arrange
        nodes = [DummyNode(f"Node{i}") for i in range(10)]

        # Act
        head = chain(*nodes)

        # Assert
        assert head is nodes[0]
        current = head
        for i, node in enumerate(nodes):
            assert current is node
            if i < len(nodes) - 1:
                assert current.next is nodes[i + 1]
            current = current.next

    async def test_single_node_returns_itself(self):
        # Arrange
        node = DummyNode("A")

        # Act
        head = chain(node)

        # Assert
        assert head is node
        assert node.next is None
        assert node.previous is None

    async def test_raises_error_on_empty_chain(self):
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Cannot build empty chain"):
            chain()

    async def test_maintains_chain_integrity(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")
        node3 = DummyNode("C")
        node4 = DummyNode("D")

        # Act
        head = chain(node1, node2, node3, node4)

        # Assert - walk forward
        current = head
        names_forward = []
        while current:
            names_forward.append(current.name)
            if current.next:
                assert current.next.previous is current
            current = current.next

        assert names_forward == ["A", "B", "C", "D"]


@pytest.mark.asyncio
class TestChain:
    """Test suite for Chain class."""

    async def test_builds_simple_chain(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")
        node3 = DummyNode("C")

        # Act
        head = Chain().add(node1).add(node2).add(node3).build()

        # Assert
        assert head is node1
        assert node1.next is node2
        assert node2.next is node3

    async def test_constructor_with_nodes(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")
        node3 = DummyNode("C")

        # Act
        head = Chain(node1, node2, node3).build()

        # Assert
        assert head is node1
        assert node1.next is node2
        assert node2.next is node3

    async def test_add_section_adds_multiple_nodes(self):
        # Arrange
        node1 = DummyNode("A")
        nodes = [DummyNode("B"), DummyNode("C"), DummyNode("D")]

        # Act
        head = Chain().add(node1).add_section(nodes).build()

        # Assert
        assert head is node1
        assert node1.next is nodes[0]
        assert nodes[0].next is nodes[1]
        assert nodes[1].next is nodes[2]

    async def test_add_if_true_adds_node(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")
        node3 = DummyNode("C")

        # Act
        head = Chain().add(node1).add_if(True, node2).add(node3).build()

        # Assert
        assert head is node1
        assert node1.next is node2
        assert node2.next is node3

    async def test_add_if_false_skips_node(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")
        node3 = DummyNode("C")

        # Act
        head = Chain().add(node1).add_if(False, node2).add(node3).build()

        # Assert
        assert head is node1
        assert node1.next is node3
        assert node2.next is None

    async def test_raises_error_on_empty_build(self):
        # Arrange
        c = Chain()

        # Act & Assert
        with pytest.raises(ValueError, match="Cannot build empty chain"):
            c.build()

    async def test_fluent_interface_returns_self(self):
        # Arrange
        c = Chain()
        node = DummyNode("A")

        # Act & Assert
        assert c.add(node) is c
        assert c.add_section([]) is c
        assert c.add_if(True, DummyNode("B")) is c

    async def test_complex_conditional_workflow(self):
        # Arrange
        enable_feature_a = True
        enable_feature_b = False
        enable_feature_c = True

        start = DummyNode("Start")
        feature_a = DummyNode("FeatureA")
        feature_b = DummyNode("FeatureB")
        feature_c = DummyNode("FeatureC")
        end = DummyNode("End")

        # Act
        head = (
            Chain()
            .add(start)
            .add_if(enable_feature_a, feature_a)
            .add_if(enable_feature_b, feature_b)
            .add_if(enable_feature_c, feature_c)
            .add(end)
            .build()
        )

        # Assert - only A and C should be in chain
        assert head is start
        assert start.next is feature_a
        assert feature_a.next is feature_c
        assert feature_c.next is end
        assert feature_b.next is None

    async def test_mixed_add_methods(self):
        # Arrange
        node1 = DummyNode("A")
        nodes_section = [DummyNode("B"), DummyNode("C")]
        node4 = DummyNode("D")
        node5 = DummyNode("E")

        # Act
        head = (
            Chain()
            .add(node1)
            .add_section(nodes_section)
            .add_if(True, node4)
            .add(node5)
            .build()
        )

        # Assert
        assert head is node1
        current = head
        expected_names = ["A", "B", "C", "D", "E"]
        for expected_name in expected_names:
            assert current.name == expected_name
            current = current.next

    async def test_single_node_builder(self):
        # Arrange
        node = DummyNode("A")

        # Act
        head = Chain().add(node).build()

        # Assert
        assert head is node
        assert node.next is None

    async def test_single_node_constructor(self):
        # Arrange
        node = DummyNode("A")

        # Act
        head = Chain(node).build()

        # Assert
        assert head is node
        assert node.next is None

    async def test_builder_with_empty_section(self):
        # Arrange
        node1 = DummyNode("A")
        node2 = DummyNode("B")

        # Act
        head = Chain().add(node1).add_section([]).add(node2).build()

        # Assert
        assert head is node1
        assert node1.next is node2
