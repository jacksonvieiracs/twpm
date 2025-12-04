from typing import override

from midnight.core.base import ListData, Node, NodeResult
from midnight.core.decorators import safe_execute


class QuestionNode(Node):
    """
    Node that asks a question and waits for user input.

    This node displays a question prompt and stores the user's response
    in the workflow data using the specified key.
    """

    def __init__(self, question: str, key: str):
        """
        Initialize a QuestionNode.

        Args:
            question: The question to ask the user
            key: The key to store the answer in the workflow data
        """
        super().__init__()
        self.question = question
        self.key = key
        self._waiting_for_input = True

    @override
    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        """
        Ask the question and process the user's input.

        On first execution, displays the question and waits for input.
        On subsequent execution (after input is provided), stores the answer.

        Args:
            data: Shared workflow data

        Returns:
            NodeResult indicating the node is awaiting input or has completed
        """
        if self._waiting_for_input:
            # First execution: display the question and wait for input
            print(f"\n? {self.question}:", end=" ")
            self._waiting_for_input = False

            return NodeResult(
                success=True,
                data={},
                message=f"Waiting for answer to: {self.question}",
                is_awaiting_input=True,
            )
        # Second execution: process the user's input
        user_input = data.get("_user_input", "")
        data[self.key] = user_input

        return NodeResult(
            success=True,
            data={},
            message=f"Stored answer for: {self.question}",
            is_awaiting_input=False,
        )
