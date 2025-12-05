import pytest
from nodes import DisplayMessageNode

from twpm.core.base.models import ListData


@pytest.mark.asyncio
class TestDisplayMessageNode:
    """Test suite for DisplayMessageNode."""

    async def test_executes_successfully(self):
        # Arrange
        node = DisplayMessageNode(message="Test message", key="test_msg")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success

    async def test_does_not_await_input(self):
        # Arrange
        node = DisplayMessageNode(message="Test message", key="test_msg")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert not result.is_awaiting_input

    async def test_preserves_message_in_result(self):
        # Arrange
        message = "Important message"
        node = DisplayMessageNode(message=message, key="test_msg")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.message == message
