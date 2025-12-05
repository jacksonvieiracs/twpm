from collections.abc import Awaitable
from typing import Callable, override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.decorators import safe_execute

AsyncTaskFunc = Callable[[ListData], Awaitable[bool]]


class TaskNode(Node):
    def __init__(self, async_task_func: AsyncTaskFunc):
        self.async_task_func: AsyncTaskFunc = async_task_func
        super().__init__()

    @override
    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        success = await self.async_task_func(data)
        result = NodeResult(success=success, data={}, message="")
        return result
