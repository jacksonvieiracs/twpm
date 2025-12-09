from collections.abc import Awaitable, Callable
from typing import override

from twpm.core.base import ListData, Node, NodeResult
from twpm.core.decorators import safe_execute
from twpm.core.depedencies import Output

_SELECT_PROMPT = "Select an option (1-{}):"


class PoolOption:
    display_text: str
    value: str

    def __init__(self, display_text: str, value: str | None = None):
        self.display_text = display_text
        self.value = value if value is not None else display_text


AsyncPoolOptionsFunc = Callable[[ListData], Awaitable[list[PoolOption]]]
PoolOptionsInput = list[PoolOption] | AsyncPoolOptionsFunc


class PoolNode(Node):
    """
    Node that presents a list of options for the user to choose from.

    This node displays a question with multiple choice options and stores
    the user's selection in the workflow data.
    """

    def __init__(self, question: str, options: PoolOptionsInput, key: str):
        """
        Initialize a PoolNode.

        Args:
            question: The question to ask the user
            options: List of options to present to the user
            key: The key to store the selected option in the workflow data
        """
        super().__init__(key)
        self.question = question
        self.options: list[PoolOption] = []
        self._options_input = options
        self._options_loaded = False
        self._waiting_for_input = True

        if isinstance(options, list):
            self.options = options
            self._options_loaded = True

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
            if not self._options_loaded:
                assert callable(self._options_input), (
                    "Options input must be callable if not pre-loaded"
                )
                self.options = await self._options_input(data)
                self._options_loaded = True

            message = ""
            message += f"\n? {self.question}:\n"
            for i, option in enumerate(self.options, 1):
                message += f"  {i}. {option}\n"

            message += _SELECT_PROMPT.format(len(self.options))
            await output.send_text(message)

            self._waiting_for_input = False

            return NodeResult(
                success=True,
                data={},
                message=f"Waiting for selection from: {self.question}",
                is_awaiting_input=True,
            )

        user_input = data.get("_user_input", "")
        assert user_input is not None, "User input is required here"

        try:
            index = int(user_input.strip()) - 1
            if 0 <= index < len(self.options):
                data[self.key] = self.options[index].value

                return NodeResult(
                    success=True,
                    data={},
                    message=f"Selected option: {self.options[index]}",
                    is_awaiting_input=False,
                )

            max_opt = len(self.options)
            await output.send_text(_SELECT_PROMPT.format(max_opt))

            return NodeResult(
                success=True,
                data={},
                message="Invalid selection, waiting for valid input",
                is_awaiting_input=True,
            )
        except ValueError:
            await output.send_text("Invalid input. Please enter a number.")

            return NodeResult(
                success=True,
                data={},
                message="Invalid input format, waiting for valid input",
                is_awaiting_input=True,
            )
