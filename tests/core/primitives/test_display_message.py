import pytest

from twpm.core.base.models import ListData
from twpm.core.primitives import DisplayMessageNode


class MockOutput:
    def __init__(self):
        self.messages = []

    async def send_text(self, text: str) -> None:
        self.messages.append(text)


@pytest.mark.asyncio
class TestDisplayMessageNode:
    async def test_executes_successfully(self):
        node = DisplayMessageNode(message="Test message", key="test_msg")
        data = ListData(data={})
        output = MockOutput()

        result = await node.execute(data, output)

        assert result.success

    async def test_does_not_await_input(self):
        node = DisplayMessageNode(message="Test message", key="test_msg")
        data = ListData(data={})
        output = MockOutput()

        result = await node.execute(data, output)

        assert not result.is_awaiting_input

    async def test_preserves_message_in_result(self):
        message = "Important message"
        node = DisplayMessageNode(message=message, key="test_msg")
        data = ListData(data={})
        output = MockOutput()

        result = await node.execute(data, output)

        assert result.message == message

    async def test_uses_message_func_if_provided(self):
        def message_func(data: ListData) -> str:
            return f"Hello, {data.get('name')}!"

        node = DisplayMessageNode(key="test_msg", message_func=message_func)
        data = ListData(data={"name": "John Doe"})
        output = MockOutput()
        result = await node.execute(data, output)
        assert result.message == "Hello, John Doe!"

    async def test_raises_error_if_no_message_or_message_func_is_provided(self):
        with pytest.raises(
            ValueError, match="Either message or message_func must be provided."
        ):
            DisplayMessageNode(key="test_msg")
