from typing import override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.decorators import safe_execute


class SummaryNode(Node):
    """
    Node that displays a summary of collected data with a nice formatted output.

    This node shows all the collected answers in a formatted way with checkmarks.
    """

    def __init__(
        self,
        title: str,
        fields: list[tuple[str, str]],
        key: str | None = None,
    ):
        """
        Initialize a SummaryNode.

        Args:
            title: The title message to display before the summary
            fields: List of tuples (label, data_key) to display in the summary
            key: Optional unique key for this node
        """
        super().__init__()
        self.title = title
        self.fields = fields
        if key:
            self.key = key

    @override
    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        """
        Display the summary of collected data.

        Args:
            data: Shared workflow data containing all collected answers

        Returns:
            NodeResult indicating success with the displayed summary
        """
        print(f"\n{self.title}\n")

        for _, data_key in self.fields:
            value = data.get(data_key, "N/A")
            print(f"✅ {value}")

        return NodeResult(
            success=True, data={}, message="Summary displayed", is_awaiting_input=False
        )
