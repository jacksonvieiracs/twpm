import pytest

from twpm.core.base import ListData, NodeResult, NodeStatus
from twpm.core.primitives.task import TaskNode


@pytest.mark.asyncio
class TestTaskNode:
    """Test suite for TaskNode."""

    async def test_task_node_success(self):
        """Test task node with successful execution."""

        async def successful_task(data: ListData) -> bool:
            return True

        node = TaskNode(successful_task)
        data = ListData(data={})

        result = await node.execute(data)

        assert result.success is True
        assert isinstance(result, NodeResult)

    async def test_task_node_failure(self):
        """Test task node with failed execution."""

        async def failing_task(data: ListData) -> bool:
            return False

        node = TaskNode(failing_task)
        data = ListData(data={})

        result = await node.execute(data)

        assert result.success is False

    async def test_task_node_with_data_access(self):
        """Test task node that accesses shared data."""

        async def data_access_task(data: ListData) -> bool:
            value = data.get("test_key")
            return value == "expected_value"

        node = TaskNode(data_access_task)
        data = ListData(data={"test_key": "expected_value"})

        result = await node.execute(data)

        assert result.success is True

    async def test_task_node_with_computation(self):
        """Test task node that performs computation."""
        call_count = 0

        async def computation_task(data: ListData) -> bool:
            nonlocal call_count
            call_count += 1
            return True

        node = TaskNode(computation_task)
        data = ListData(data={})

        await node.execute(data)

        assert call_count == 1

    async def test_task_node_initial_status(self):
        """Test that task node has correct initial status."""

        async def dummy_task(data: ListData) -> bool:
            return True

        node = TaskNode(dummy_task)

        assert node.status == NodeStatus.DEFAULT
        assert node.next is None
        assert node.previous is None

    async def test_task_node_returns_empty_data(self):
        """Test that task node returns empty data dict by default."""

        async def dummy_task(data: ListData) -> bool:
            return True

        node = TaskNode(dummy_task)
        data = ListData(data={})

        result = await node.execute(data)

        assert result.data == {}

    async def test_task_node_returns_empty_message(self):
        """Test that task node returns empty message by default."""

        async def dummy_task(data: ListData) -> bool:
            return True

        node = TaskNode(dummy_task)
        data = ListData(data={})

        result = await node.execute(data)

        assert result.message == ""

    async def test_task_node_chaining(self):
        """Test that task nodes can be chained."""

        async def task1(data: ListData) -> bool:
            return True

        async def task2(data: ListData) -> bool:
            return True

        node1 = TaskNode(task1)
        node2 = TaskNode(task2)

        node1.next = node2
        node2.previous = node1

        assert node1.next == node2
        assert node2.previous == node1

    async def test_task_node_with_exception(self):
        """Test task node behavior when function raises exception - should return failed result."""

        async def exception_task(data: ListData) -> bool:
            raise ValueError("Test exception")

        node = TaskNode(exception_task)
        data = ListData(data={})

        # Should not raise - decorator catches exception and returns failed result
        result = await node.execute(data)

        assert result.success is False
        assert "Test exception" in result.message
        assert result.is_awaiting_input is False

    async def test_task_node_complex_logic(self):
        """Test task node with complex conditional logic."""

        async def complex_task(data: ListData) -> bool:
            value_a = data.get("a")
            value_b = data.get("b")

            if value_a and value_b:
                return int(value_a) + int(value_b) == 10
            return False

        node = TaskNode(complex_task)
        data = ListData(data={"a": "4", "b": "6"})

        result = await node.execute(data)

        assert result.success is True

        # Test with different values
        data2 = ListData(data={"a": "3", "b": "6"})
        result2 = await node.execute(data2)

        assert result2.success is False
