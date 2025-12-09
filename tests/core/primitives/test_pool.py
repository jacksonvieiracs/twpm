import pytest

from twpm.core.base.models import ListData
from twpm.core.primitives import PoolNode, PoolOption


class MockOutput:
    def __init__(self):
        self.messages = []

    async def send_text(self, text: str) -> None:
        self.messages.append(text)


@pytest.mark.asyncio
class TestPoolNode:
    async def test_first_execution_awaits_input(self):
        node = PoolNode(
            question="Color?",
            options=[PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")],
            key="color",
        )
        data = ListData(data={})
        output = MockOutput()

        result = await node.execute(data, output)

        assert result.is_awaiting_input

    async def test_first_execution_succeeds(self):
        node = PoolNode(
            question="Color?",
            options=[PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")],
            key="color",
        )
        data = ListData(data={})
        output = MockOutput()

        result = await node.execute(data, output)

        assert result.success

    async def test_stores_selected_option_by_index(self):
        node = PoolNode(
            question="Color?",
            options=[PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")],
            key="color",
        )
        data = ListData(data={})
        output = MockOutput()
        await node.execute(data, output)
        data["_user_input"] = "2"

        await node.execute(data, output)

        assert data["color"] == "Blue"

    async def test_second_execution_does_not_await_input_on_valid_selection(self):
        node = PoolNode(
            question="Color?",
            options=[PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")],
            key="color",
        )
        data = ListData(data={})
        output = MockOutput()
        await node.execute(data, output)
        data["_user_input"] = "1"

        result = await node.execute(data, output)

        assert not result.is_awaiting_input

    async def test_rejects_out_of_range_selection(self):
        node = PoolNode(
            question="Color?",
            options=[PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")],
            key="color",
        )
        data = ListData(data={})
        output = MockOutput()
        await node.execute(data, output)
        data["_user_input"] = "5"

        result = await node.execute(data, output)

        assert result.is_awaiting_input

    async def test_rejects_non_numeric_input(self):
        node = PoolNode(
            question="Color?",
            options=[PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")],
            key="color",
        )
        data = ListData(data={})
        output = MockOutput()
        await node.execute(data, output)
        data["_user_input"] = "abc"

        result = await node.execute(data, output)

        assert result.is_awaiting_input

    async def test_rejects_zero_selection(self):
        node = PoolNode(
            question="Color?",
            options=[PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")],
            key="color",
        )
        data = ListData(data={})
        output = MockOutput()
        await node.execute(data, output)
        data["_user_input"] = "0"

        result = await node.execute(data, output)

        assert result.is_awaiting_input

    async def test_load_options_lazy(self):
        async def load_options_lazy(data: ListData):
            return [PoolOption("Red"), PoolOption("Blue"), PoolOption("Green")]

        node = PoolNode(
            question="Color?",
            options=load_options_lazy,
            key="color",
        )

        data = ListData(data={})
        output = MockOutput()

        assert node._options_loaded == False
        assert len(node.options) == 0

        await node.execute(data, output)

        assert node._options_loaded
        assert len(node.options) == 3
