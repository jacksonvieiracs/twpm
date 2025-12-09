from collections.abc import Callable
from typing import override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.decorators import safe_execute
from twpm.core.depedencies import Output

SyncPoolOptionsFunc = Callable[[ListData], str]


class DisplayMessageNode(Node):
    """
    Node that displays a message to the user without expecting input.

    This node simply prints a message and continues to the next node.
    """

    def __init__(
        self,
        key: str,
        message: str | None = None,
        message_func: SyncPoolOptionsFunc | None = None,
    ):
        """
        Initialize a DisplayMessageNode.

        Args:
            message: The message to display to the user
            key: Unique key for this node (default: "display_message")
        """
        super().__init__(key)
        self._message_loaded = False
        self._message_func = message_func
        self._message = message

        if message is None and message_func is None:
            raise ValueError("Either message or message_func must be provided.")

        if message is not None:
            self._message = message
            self._message_loaded = True

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
        if not self._message_loaded:
            self._message = self._message_func(data)
            self._message_loaded = True

        await output.send_text(self._message)

        return NodeResult(
            success=True, data={}, message=self._message, is_awaiting_input=False
        )
