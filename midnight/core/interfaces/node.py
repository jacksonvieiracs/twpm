from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class NodeResult:
    success: bool
    data: dict[str, str]
    message: str


class Node(ABC):
    def __init__(self) -> None:
        self.next: "Node | None" = None
        self.previous: "Node | None" = None

    @abstractmethod
    async def execute(self) -> NodeResult: ...
