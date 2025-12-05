from typing import override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.decorators import safe_execute
from twpm.core.depedencies import Output


class ProgressNode(Node):
    """
    Node that displays workflow progress.

    Shows completed fields with their values (✅) and pending fields
    with their labels (☑️). Useful for multi-step forms and questionnaires.
    """

    def __init__(
        self,
        fields: list[tuple[str, str]],
        title: str | None = None,
        key: str | None = None,
    ):
        """
        Initialize a ProgressNode.

        Args:
            fields: List of tuples (label, data_key) representing the fields to track
            title: Optional title to display before the progress list
            key: Optional unique key for this node
        """
        super().__init__()
        self.fields = fields
        self.title = title
        if key:
            self.key = key

    @override
    @safe_execute()
    async def execute(self, data: ListData, output: Output) -> NodeResult:
        """
        Display the progress of data collection.

        Args:
            data: Shared workflow data

        Returns:
            NodeResult indicating success with the displayed progress
        """
        message = ""

        if self.title:
            message += f"\n{self.title}\n"
        else:
            message += "\n"

        for label, data_key in self.fields:
            value = data.get(data_key)
            if value is not None:
                # Field has been completed - show the value
                message += f"✅ {value}\n"
            else:
                # Field is pending - show the label
                message += f"☑️ {label}\n"

        output.send_text(message)

        return NodeResult(
            success=True, data={}, message="Progress displayed", is_awaiting_input=False
        )
