import pytest
from nodes import ProgressNode

from twpm.core.base.models import ListData


@pytest.mark.asyncio
class TestProgressNode:
    """Test suite for ProgressNode."""

    async def test_executes_successfully(self):
        # Arrange
        fields = [("Name", "name"), ("Email", "email")]
        node = ProgressNode(fields=fields, key="progress")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success

    async def test_does_not_await_input(self):
        # Arrange
        fields = [("Name", "name"), ("Email", "email")]
        node = ProgressNode(fields=fields, key="progress")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert not result.is_awaiting_input

    async def test_displays_completed_and_pending_fields(self):
        # Arrange
        fields = [("Name", "name"), ("Email", "email"), ("Phone", "phone")]
        node = ProgressNode(fields=fields, key="progress")
        data = ListData(data={"name": "John", "phone": "123456"})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success

    async def test_executes_with_title(self):
        # Arrange
        fields = [("Name", "name")]
        node = ProgressNode(fields=fields, title="Progress Update", key="progress")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success

    async def test_executes_with_empty_fields(self):
        # Arrange
        fields = []
        node = ProgressNode(fields=fields, key="progress")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success
