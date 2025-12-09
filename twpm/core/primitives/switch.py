from typing import Callable, override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.cursor import Cursor
from twpm.core.decorators import safe_execute

SwitchFunc = Callable[[ListData], str]


class SwitchNode(Node):
    def __init__(self, key: str = "switch"):
        self.switch_func: SwitchFunc | None = None
        self.case_nodes: dict[str, Node] = {}
        self.default_node: Node | None = None
        super().__init__(key)

    @override
    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        if self.switch_func is None:
            raise ValueError("Condition function is not set.")

        case = self.switch_func(data)
        if case in self.case_nodes:
            next_node = self.case_nodes[case]
        else:
            next_node = self.default_node

        assert next_node is not None, "Next node is not set."
        Cursor.insert(self, next_node)

        result = NodeResult(success=True, data={}, message="")
        return result

    def set_switch(
        self,
        condition_func: SwitchFunc,
        case_nodes: dict[str, Node],
        default_node: Node,
    ) -> None:
        self.switch_func = condition_func
        self.case_nodes = case_nodes
        self.default_node = default_node
