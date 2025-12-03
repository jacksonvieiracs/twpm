from collections.abc import Awaitable
from typing import Callable, override
from midnight.core.interfaces.node import ListData, Node, NodeResult

AsyncTaskFunc = Callable[[ListData], Awaitable[bool]]


class TaskNode(Node):
    def __init__(self, async_task_func: AsyncTaskFunc):
        self.async_task_func: AsyncTaskFunc = async_task_func
        super().__init__()

    @override
    async def execute(self, data: ListData) -> NodeResult:
        success = await self.async_task_func(data)
        result = NodeResult(success=success, data={}, message="")
        return result
