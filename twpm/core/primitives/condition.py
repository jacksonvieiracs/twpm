from typing import Callable, override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.cursor import Cursor
from twpm.core.decorators import safe_execute

ConditionalFunc = Callable[[ListData], bool]


class ConditionalNode(Node):
    def __init__(self):
        self.condition_func: ConditionalFunc | None = None
        self.true_node: Node | None = None
        self.false_node: Node | None = None
        super().__init__()

    @override
    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        if self.condition_func is None:
            raise ValueError("Condition function is not set.")

        if self.condition_func(data):
            next_node = self.true_node
        else:
            next_node = self.false_node

        assert next_node is not None, "Next node is not set."
        Cursor.insert(self, next_node)

        result = NodeResult(success=True, data={}, message="")
        return result

    def set_condition(
        self, condition_func: ConditionalFunc, true_node: Node, false_node: Node
    ) -> None:
        self.condition_func = condition_func
        self.true_node = true_node
        self.false_node = false_node
