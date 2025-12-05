import pytest
from nodes import PoolNode

from twpm.core.base.models import ListData


@pytest.mark.asyncio
class TestPoolNode:
    """Test suite for PoolNode."""

    async def test_first_execution_awaits_input(self):
        # Arrange
        node = PoolNode(
            question="Color?", options=["Red", "Blue", "Green"], key="color"
        )
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.is_awaiting_input

    async def test_first_execution_succeeds(self):
        # Arrange
        node = PoolNode(
            question="Color?", options=["Red", "Blue", "Green"], key="color"
        )
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success

    async def test_stores_selected_option_by_index(self):
        # Arrange
        node = PoolNode(
            question="Color?", options=["Red", "Blue", "Green"], key="color"
        )
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "2"

        # Act
        await node.execute(data)

        # Assert
        assert data["color"] == "Blue"

    async def test_second_execution_does_not_await_input_on_valid_selection(self):
        # Arrange
        node = PoolNode(
            question="Color?", options=["Red", "Blue", "Green"], key="color"
        )
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "1"

        # Act
        result = await node.execute(data)

        # Assert
        assert not result.is_awaiting_input

    async def test_rejects_out_of_range_selection(self):
        # Arrange
        node = PoolNode(
            question="Color?", options=["Red", "Blue", "Green"], key="color"
        )
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "5"

        # Act
        result = await node.execute(data)

        # Assert
        assert result.is_awaiting_input

    async def test_rejects_non_numeric_input(self):
        # Arrange
        node = PoolNode(
            question="Color?", options=["Red", "Blue", "Green"], key="color"
        )
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "abc"

        # Act
        result = await node.execute(data)

        # Assert
        assert result.is_awaiting_input

    async def test_rejects_zero_selection(self):
        # Arrange
        node = PoolNode(
            question="Color?", options=["Red", "Blue", "Green"], key="color"
        )
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "0"

        # Act
        result = await node.execute(data)

        # Assert
        assert result.is_awaiting_input
