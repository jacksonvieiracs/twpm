from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NodeResult:
    success: bool
    data: dict[str, str]
    message: str


NodeKey = str
Value = str


@dataclass
class ListData:
    data: dict[NodeKey, Value]

    def __getitem__(self, key: NodeKey) -> Value:
        return self.data[key]

    # set a value based of the result

    def get(self, key: NodeKey, default: Value | None):
        return self.data.get(key, default)


class Node(ABC):
    def __init__(self) -> None:
        self.key: NodeKey
        self.next: "Node | None" = None
        self.previous: "Node | None" = None

    @abstractmethod
    async def execute(self, data: ListData) -> NodeResult: ...
