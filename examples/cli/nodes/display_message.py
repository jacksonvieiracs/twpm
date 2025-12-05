from typing import override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.decorators import safe_execute
from twpm.core.depedencies import Output


class DisplayMessageNode(Node):
    """
    Node that displays a message to the user without expecting input.

    This node simply prints a message and continues to the next node.
    """

    def __init__(self, message: str, key: str | None = None):
        """
        Initialize a DisplayMessageNode.

        Args:
            message: The message to display to the user
            key: Optional unique key for this node
        """
        super().__init__()
        self.message = message
        if key:
            self.key = key

    @override
    @safe_execute()
    async def execute(self, data: ListData, output: Output) -> NodeResult:
        """
        Display the message to the user.

        Args:
            data: Shared workflow data

        Returns:
            NodeResult indicating success with the displayed message
        """
        output.send_text(f"\n{self.message}")

        return NodeResult(
            success=True, data={}, message=self.message, is_awaiting_input=False
        )
