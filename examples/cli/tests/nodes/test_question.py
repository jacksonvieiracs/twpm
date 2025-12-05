import pytest
from nodes import QuestionNode

from twpm.core.base.models import ListData


@pytest.mark.asyncio
class TestQuestionNode:
    """Test suite for QuestionNode."""

    async def test_first_execution_awaits_input(self):
        # Arrange
        node = QuestionNode(question="Your name?", key="name")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.is_awaiting_input

    async def test_first_execution_succeeds(self):
        # Arrange
        node = QuestionNode(question="Your name?", key="name")
        data = ListData(data={})

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success

    async def test_stores_user_input_on_second_execution(self):
        # Arrange
        node = QuestionNode(question="Your name?", key="name")
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "John Doe"

        # Act
        await node.execute(data)

        # Assert
        assert data["name"] == "John Doe"

    async def test_second_execution_does_not_await_input(self):
        # Arrange
        node = QuestionNode(question="Your name?", key="name")
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "John Doe"

        # Act
        result = await node.execute(data)

        # Assert
        assert not result.is_awaiting_input

    async def test_second_execution_succeeds(self):
        # Arrange
        node = QuestionNode(question="Your name?", key="name")
        data = ListData(data={})
        await node.execute(data)
        data["_user_input"] = "John Doe"

        # Act
        result = await node.execute(data)

        # Assert
        assert result.success
