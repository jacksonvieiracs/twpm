from abc import ABC, abstractmethod
import asyncio

from dataclasses import dataclass
from random import randint
from typing import Self


@dataclass
class NodeStorage:
    nodes: dict[str, dict[str, str]]

    def set_result(self, key: str, data: dict[str, str]):
        self.nodes[key] = data


@dataclass
class NodeResult:
    success: bool
    data: dict[str, str]
    message: str


success_result = NodeResult(success=True, data={}, message="")


class Node(ABC):
    next: Self | None = None

    @abstractmethod
    async def execute(self) -> NodeResult: ...

    def set_next(self, next: Self):
        self.next = next


class ActionNode(Node):
    next: Node | None = None

    async def execute(self) -> NodeResult:
        print("hello")

    def set_next(self, next: Node):
        self.next = next


class ConditionNode(Node):
    async def execute(self) -> NodeResult:
        path1 = ActionNode()
        path2 = ActionNode()
        if randint(1, 2) % 2 == 0:
            self.set_next(path1)
        else:
            self.set_next(path2)
        return success_result


if __name__ == "__main__":
    action_node = ActionNode()
    condition_node = ConditionNode()

    current_node = condition_node

    while current_node != None:
        asyncio.run(current_node.execute())
        current_node = current_node.next
