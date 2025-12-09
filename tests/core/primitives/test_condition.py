import pytest

from twpm.core.base import ListData, NodeResult, NodeStatus
from twpm.core.primitives.condition import ConditionalNode
from twpm.core.primitives.task import TaskNode


@pytest.mark.asyncio
class TestConditionalNode:
    """Test suite for ConditionalNode."""

    async def test_conditional_node_true_branch(self):
        """Test conditional node takes true branch when condition is true."""

        async def always_true_task(data: ListData) -> bool:
            return True

        async def never_executed_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(always_true_task, key="true_node")
        false_node = TaskNode(never_executed_task, key="false_node")

        def true_condition(data: ListData) -> bool:
            return True

        cond_node = ConditionalNode()
        cond_node.set_condition(true_condition, true_node, false_node)

        data = ListData(data={})
        result = await cond_node.execute(data)

        assert result.success is True
        assert cond_node.next == true_node

    async def test_conditional_node_false_branch(self):
        """Test conditional node takes false branch when condition is false."""

        async def never_executed_task(data: ListData) -> bool:
            return True

        async def always_true_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(never_executed_task, key="true_node")
        false_node = TaskNode(always_true_task, key="false_node")

        def false_condition(data: ListData) -> bool:
            return False

        cond_node = ConditionalNode()
        cond_node.set_condition(false_condition, true_node, false_node)

        data = ListData(data={})
        result = await cond_node.execute(data)

        assert result.success is True
        assert cond_node.next == false_node

    async def test_conditional_node_with_data_check(self):
        """Test conditional node with data-based condition."""

        async def dummy_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(dummy_task, key="true_node")
        false_node = TaskNode(dummy_task, key="false_node")

        def data_condition(data: ListData) -> bool:
            value = data.get("check_value")
            return value == "expected"

        cond_node = ConditionalNode()
        cond_node.set_condition(data_condition, true_node, false_node)

        data_match = ListData(data={"check_value": "expected"})
        _ = await cond_node.execute(data_match)
        assert cond_node.next == true_node

        cond_node2 = ConditionalNode()
        cond_node2.set_condition(data_condition, true_node, false_node)
        data_no_match = ListData(data={"check_value": "other"})
        _ = await cond_node2.execute(data_no_match)
        assert cond_node2.next == false_node

    async def test_conditional_node_without_condition_raises_error(self):
        """Test that executing without setting condition returns failed result."""
        cond_node = ConditionalNode()
        data = ListData(data={})

        result = await cond_node.execute(data)

        assert result.success is False
        assert "Condition function is not set" in result.message

    async def test_conditional_node_initial_state(self):
        """Test conditional node initial state."""
        cond_node = ConditionalNode()

        assert cond_node.condition_func is None
        assert cond_node.true_node is None
        assert cond_node.false_node is None
        assert cond_node.status == NodeStatus.DEFAULT

    async def test_set_condition_updates_properties(self):
        """Test that set_condition properly updates all properties."""

        async def dummy_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(dummy_task, key="true_node")
        false_node = TaskNode(dummy_task, key="false_node")

        def condition(data: ListData) -> bool:
            return True

        cond_node = ConditionalNode()
        cond_node.set_condition(condition, true_node, false_node)

        assert cond_node.condition_func == condition
        assert cond_node.true_node == true_node
        assert cond_node.false_node == false_node

    async def test_conditional_node_returns_success(self):
        """Test that conditional node always returns success."""

        async def dummy_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(dummy_task, key="true_node")
        false_node = TaskNode(dummy_task, key="false_node")

        def condition(data: ListData) -> bool:
            return True

        cond_node = ConditionalNode()
        cond_node.set_condition(condition, true_node, false_node)

        data = ListData(data={})
        result = await cond_node.execute(data)

        assert result.success is True
        assert isinstance(result, NodeResult)

    async def test_conditional_node_returns_empty_data(self):
        """Test that conditional node returns empty data."""

        async def dummy_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(dummy_task, key="true_node")
        false_node = TaskNode(dummy_task, key="false_node")

        def condition(data: ListData) -> bool:
            return True

        cond_node = ConditionalNode()
        cond_node.set_condition(condition, true_node, false_node)

        data = ListData(data={})
        result = await cond_node.execute(data)

        assert result.data == {}
        assert result.message == ""

    async def test_conditional_node_complex_condition(self):
        """Test conditional node with complex condition logic."""

        async def dummy_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(dummy_task, key="true_node")
        false_node = TaskNode(dummy_task, key="false_node")

        def complex_condition(data: ListData) -> bool:
            a = data.get("a")
            b = data.get("b")

            if a and b:
                return int(a) > int(b)
            return False

        cond_node = ConditionalNode()
        cond_node.set_condition(complex_condition, true_node, false_node)

        data_true = ListData(data={"a": "10", "b": "5"})
        _ = await cond_node.execute(data_true)
        assert cond_node.next == true_node

        cond_node2 = ConditionalNode()
        cond_node2.set_condition(complex_condition, true_node, false_node)
        data_false = ListData(data={"a": "3", "b": "8"})
        _ = await cond_node2.execute(data_false)
        assert cond_node2.next == false_node

    async def test_conditional_node_chaining(self):
        """Test that conditional nodes can be part of a chain."""

        async def dummy_task(data: ListData) -> bool:
            return True

        pre_node = TaskNode(dummy_task, key="pre_node")
        true_node = TaskNode(dummy_task, key="true_node")
        false_node = TaskNode(dummy_task, key="false_node")

        def condition(data: ListData) -> bool:
            return True

        cond_node = ConditionalNode()
        cond_node.set_condition(condition, true_node, false_node)

        pre_node.next = cond_node
        cond_node.previous = pre_node

        assert pre_node.next == cond_node
        assert cond_node.previous == pre_node

    async def test_conditional_node_exception_in_condition(self):
        """Test that exceptions in condition function are caught by decorator."""

        async def dummy_task(data: ListData) -> bool:
            return True

        true_node = TaskNode(dummy_task, key="true_node")
        false_node = TaskNode(dummy_task, key="false_node")

        def failing_condition(data: ListData) -> bool:
            raise RuntimeError("Condition evaluation failed")

        cond_node = ConditionalNode()
        cond_node.set_condition(failing_condition, true_node, false_node)

        data = ListData(data={})

        result = await cond_node.execute(data)

        assert result.success is False
        assert "Condition evaluation failed" in result.message
        assert result.is_awaiting_input is False
