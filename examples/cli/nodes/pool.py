from typing import override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.decorators import safe_execute
from twpm.core.depedencies import Output

_SELECT_PROMPT = "Select an option (1-{}):"


class PoolNode(Node):
    """
    Node that presents a list of options for the user to choose from.

    This node displays a question with multiple choice options and stores
    the user's selection in the workflow data.
    """

    def __init__(self, question: str, options: list[str], key: str):
        """
        Initialize a PoolNode.

        Args:
            question: The question to ask the user
            options: List of options to present to the user
            key: The key to store the selected option in the workflow data
        """
        super().__init__()
        self.question = question
        self.options = options
        self.key = key
        self._waiting_for_input = True

    @override
    @safe_execute()
    async def execute(self, data: ListData, output: Output) -> NodeResult:
        """
        Display question with options and process user selection.

        First execution: displays options, waits for input.
        Second execution: validates and stores the answer.

        Args:
            data: Shared workflow data

        Returns:
            NodeResult indicating awaiting input or completed
        """
        if self._waiting_for_input:
            message = ""
            message += f"\n? {self.question}:\n"
            for i, option in enumerate(self.options, 1):
                message += f"  {i}. {option}\n"

            message += _SELECT_PROMPT.format(len(self.options))
            output.send_text(message)

            self._waiting_for_input = False

            return NodeResult(
                success=True,
                data={},
                message=f"Waiting for selection from: {self.question}",
                is_awaiting_input=True,
            )

        # Second execution: validate and process the user's input
        user_input = data.get("_user_input", "")

        try:
            index = int(user_input.strip()) - 1
            if 0 <= index < len(self.options):
                data[self.key] = self.options[index]

                return NodeResult(
                    success=True,
                    data={},
                    message=f"Selected option: {self.options[index]}",
                    is_awaiting_input=False,
                )

            # Invalid selection, ask again
            max_opt = len(self.options)
            print(f"Invalid option. Please select 1-{max_opt}.")
            print(_SELECT_PROMPT.format(max_opt), end=" ")

            return NodeResult(
                success=True,
                data={},
                message="Invalid selection, waiting for valid input",
                is_awaiting_input=True,
            )
        except ValueError:
            # Invalid format, ask again
            print("Invalid input. Please enter a number.")
            print(_SELECT_PROMPT.format(len(self.options)), end=" ")

            return NodeResult(
                success=True,
                data={},
                message="Invalid input format, waiting for valid input",
                is_awaiting_input=True,
            )
