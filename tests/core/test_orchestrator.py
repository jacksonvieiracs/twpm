import logging

import pytest

from twpm.core.base import ListData, Node, NodeResult, NodeStatus
from twpm.core.container import Container, ServiceScope
from twpm.core.decorators import safe_execute
from twpm.core.depedencies import Output
from twpm.core.orchestrator import Orchestrator


class MockNode(Node):
    """Mock node for testing purposes."""

    def __init__(
        self,
        key: str,
        success: bool = True,
        data: dict = None,
        awaiting_input: bool = False,
    ):
        super().__init__()
        self.key = key
        self._success = success
        self._data = data or {}
        self._awaiting_input = awaiting_input
        self.execute_count = 0

    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        self.execute_count += 1
        return NodeResult(
            success=self._success,
            data=self._data,
            message=f"Node {self.key} executed",
            is_awaiting_input=self._awaiting_input,
        )


class FailingNode(Node):
    """Node that raises an exception during execution."""

    def __init__(self, key: str):
        super().__init__()
        self.key = key
        self.execute_count = 0

    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        self.execute_count += 1
        raise ValueError(f"Error in node {self.key}")


class QuestionNode(Node):
    """Node that asks a question and awaits user input."""

    def __init__(
        self,
        key: str,
        question: str,
        output_key: str = "answer",
        validate_func=None,
    ):
        super().__init__()
        self.key = key
        self.question = question
        self.output_key = output_key
        self.validate_func = validate_func
        self.execute_count = 0
        self._has_asked = False

    @safe_execute()
    async def execute(self, data: ListData) -> NodeResult:
        self.execute_count += 1

        # First execution: ask the question
        if not self._has_asked:
            self._has_asked = True
            return NodeResult(
                success=True,
                data={"question": self.question},
                message=f"Question asked: {self.question}",
                is_awaiting_input=True,
            )

        # Second execution: process the input
        user_input = data.get("_user_input")

        if user_input is None:
            return NodeResult(
                success=False,
                data={},
                message="No input provided",
                is_awaiting_input=True,
            )

        # Validate input if validator provided
        if self.validate_func and not self.validate_func(user_input):
            return NodeResult(
                success=False,
                data={},
                message=f"Invalid input: {user_input}",
                is_awaiting_input=True,
            )

        # Input is valid, store it and continue
        return NodeResult(
            success=True,
            data={self.output_key: user_input},
            message=f"Input received: {user_input}",
            is_awaiting_input=False,
        )


class MockOutput:
    """Mock output for testing purposes."""

    def __init__(self):
        self.messages = []

    def send_text(self, text: str):
        self.messages.append(text)


@pytest.fixture
def orchestrator():
    """Create a fresh orchestrator instance for each test."""
    logger = logging.getLogger("test_orchestrator")
    logger.setLevel(logging.DEBUG)

    # Create container and register mock output
    container = Container()
    container.register(Output, lambda: MockOutput(), ServiceScope.SINGLETON)

    return Orchestrator(container=container, logger=logger)


@pytest.mark.asyncio
class TestOrchestrator:
    """Test suite for the Orchestrator class."""

    async def test_orchestrator_initialization(self, orchestrator):
        """Test that orchestrator initializes correctly."""
        assert orchestrator.is_ended is False
        assert orchestrator.current_node is None

    async def test_start_sets_current_node(self, orchestrator):
        """Test that start() sets the current node."""
        node = MockNode("start")
        orchestrator.start(node)

        assert orchestrator.current_node == node

    async def test_process_without_start_raises_error(self, orchestrator):
        """Test that process() raises error if not started."""
        with pytest.raises(RuntimeError, match="Orchestrator must be started"):
            await orchestrator.process()

    async def test_single_node_execution(self, orchestrator):
        """Test executing a single successful node."""
        node = MockNode("node1", success=True, data={"result": "value1"})
        orchestrator.start(node)

        await orchestrator.process()

        assert node.execute_count == 1
        assert node.status == NodeStatus.COMPLETE
        assert orchestrator.is_ended is True

    async def test_multiple_nodes_execution(self, orchestrator):
        """Test executing a chain of nodes."""
        node1 = MockNode("node1", success=True, data={"step": "1"})
        node2 = MockNode("node2", success=True, data={"step": "2"})
        node3 = MockNode("node3", success=True, data={"step": "3"})

        node1.next = node2
        node2.next = node3

        orchestrator.start(node1)
        await orchestrator.process()

        assert node1.execute_count == 1
        assert node2.execute_count == 1
        assert node3.execute_count == 1

        assert node1.status == NodeStatus.COMPLETE
        assert node2.status == NodeStatus.COMPLETE
        assert node3.status == NodeStatus.COMPLETE

        assert orchestrator.is_ended is True

    async def test_data_merging_between_nodes(self, orchestrator):
        """Test that data from nodes is merged correctly."""
        node1 = MockNode("node1", data={"key1": "value1"})
        node2 = MockNode("node2", data={"key2": "value2"})

        node1.next = node2

        orchestrator.start(node1)
        await orchestrator.process()

        assert orchestrator._data.get("key1") == "value1"
        assert orchestrator._data.get("key2") == "value2"

    async def test_node_failure_stops_execution(self, orchestrator):
        """Test that a failing node stops the workflow."""
        node1 = MockNode("node1", success=True)
        node2 = MockNode("node2", success=False)
        node3 = MockNode("node3", success=True)

        node1.next = node2
        node2.next = node3

        orchestrator.start(node1)
        await orchestrator.process()

        assert node1.status == NodeStatus.COMPLETE
        assert node1.execute_count == 1

        assert node2.status == NodeStatus.FAILED
        assert node2.execute_count == 1

        assert node3.execute_count == 0

        assert orchestrator.is_ended is True

    async def test_awaiting_input_pauses_execution(self, orchestrator):
        """Test that awaiting_input stops processing."""
        node1 = MockNode("node1", success=True)
        node2 = MockNode("node2", success=True, awaiting_input=True)
        node3 = MockNode("node3", success=True)

        node1.next = node2
        node2.next = node3

        orchestrator.start(node1)
        await orchestrator.process()

        assert node1.execute_count == 1
        assert node2.execute_count == 1
        assert node1.status == NodeStatus.COMPLETE
        assert node2.status == NodeStatus.AWAITING_INPUT

        assert node3.execute_count == 0

        assert orchestrator.is_ended is False

        assert orchestrator.current_node == node2

    async def test_reset_functionality(self, orchestrator):
        """Test that reset() returns to the beginning."""
        node1 = MockNode("node1")
        node2 = MockNode("node2")

        node1.next = node2

        orchestrator.start(node1)
        await orchestrator.process()

        assert orchestrator.is_ended is True

        orchestrator.reset()
        assert orchestrator.is_ended is False
        assert orchestrator.current_node == node1

    async def test_exception_handling(self, orchestrator):
        """Test that exceptions in nodes are caught by decorator and returned as failed results."""
        node1 = MockNode("node1", success=True)
        node2 = FailingNode("node2")
        node3 = MockNode("node3", success=True)

        node1.next = node2
        node2.next = node3

        orchestrator.start(node1)
        await orchestrator.process()

        assert node1.status == NodeStatus.COMPLETE
        assert node1.execute_count == 1

        # Second node should execute and be marked as failed
        # (decorator catches exception and returns failed result)
        assert node2.execute_count == 1
        assert node2.status == NodeStatus.FAILED

        # Third node should not execute (workflow stopped due to failure)
        assert node3.execute_count == 0

        # Workflow should be ended
        assert orchestrator.is_ended is True

    async def test_empty_workflow(self, orchestrator):
        """Test handling of empty node (None)."""
        node = MockNode("node1")
        orchestrator.start(node)

        # Ensure node has no next
        node.next = None

        await orchestrator.process()

        assert node.execute_count == 1
        assert orchestrator.is_ended is True

    async def test_node_identifier_with_key(self, orchestrator):
        """Test that _get_node_identifier uses key when available."""
        node = MockNode("test_key")
        identifier = orchestrator._get_node_identifier(node)

        assert identifier == "test_key"

    async def test_node_identifier_without_key(self, orchestrator):
        """Test that _get_node_identifier generates fallback."""
        node = MockNode("test")
        node.key = None

        identifier = orchestrator._get_node_identifier(node)

        assert "MockNode@" in identifier

    async def test_current_node_property(self, orchestrator):
        """Test current_node property returns correct node."""
        node1 = MockNode("node1")
        node2 = MockNode("node2")
        node1.next = node2

        assert orchestrator.current_node is None

        orchestrator.start(node1)
        assert orchestrator.current_node == node1

    async def test_question_node_basic_flow(self, orchestrator):
        """Test basic question node flow: ask question, provide answer."""
        question_node = QuestionNode("ask_name", "What is your name?", "name")
        orchestrator.start(question_node)

        # First iteration: node asks question
        await orchestrator.process()

        assert question_node.execute_count == 1
        assert question_node.status == NodeStatus.AWAITING_INPUT
        assert orchestrator._data.get("question") == "What is your name?"
        assert orchestrator.is_ended is False
        assert orchestrator.current_node == question_node

        # Second iteration: provide answer
        await orchestrator.process(input="Alice")

        assert question_node.execute_count == 2
        assert question_node.status == NodeStatus.COMPLETE
        assert orchestrator._data.get("name") == "Alice"
        assert orchestrator.is_ended is True

    async def test_question_node_without_input(self, orchestrator):
        """Test question node fails when no input is provided."""
        question_node = QuestionNode("ask_age", "What is your age?", "age")
        orchestrator.start(question_node)

        # First iteration: ask question
        await orchestrator.process()

        assert question_node.execute_count == 1
        assert question_node.status == NodeStatus.AWAITING_INPUT

        # Second iteration: no input provided
        await orchestrator.process()

        assert question_node.execute_count == 2
        assert question_node.status == NodeStatus.AWAITING_INPUT
        assert orchestrator.is_ended is False

    async def test_question_node_with_validation(self, orchestrator):
        """Test question node with input validation."""

        def validate_age(value: str) -> bool:
            try:
                age = int(value)
                return 0 < age < 150
            except ValueError:
                return False

        question_node = QuestionNode(
            "ask_age", "What is your age?", "age", validate_func=validate_age
        )
        orchestrator.start(question_node)

        # First iteration: ask question
        await orchestrator.process()

        assert question_node.execute_count == 1
        assert question_node.status == NodeStatus.AWAITING_INPUT

        # Second iteration: invalid input
        await orchestrator.process(input="not a number")

        assert question_node.execute_count == 2
        assert question_node.status == NodeStatus.AWAITING_INPUT
        assert orchestrator.is_ended is False

        # Third iteration: valid input
        await orchestrator.process(input="25")

        assert question_node.execute_count == 3
        assert question_node.status == NodeStatus.COMPLETE
        assert orchestrator._data.get("age") == "25"
        assert orchestrator.is_ended is True

    async def test_multiple_question_nodes(self, orchestrator):
        """Test workflow with multiple question nodes."""
        question1 = QuestionNode("ask_name", "What is your name?", "name")
        question2 = QuestionNode("ask_email", "What is your email?", "email")
        final_node = MockNode("final", data={"status": "completed"})

        question1.next = question2
        question2.next = final_node

        orchestrator.start(question1)

        # First question - ask
        await orchestrator.process()
        assert question1.status == NodeStatus.AWAITING_INPUT
        assert orchestrator.current_node == question1

        # First question - answer
        await orchestrator.process(input="Bob")
        assert question1.status == NodeStatus.COMPLETE
        assert orchestrator._data.get("name") == "Bob"
        assert question2.status == NodeStatus.AWAITING_INPUT
        assert orchestrator.current_node == question2

        # Second question - answer
        await orchestrator.process(input="bob@example.com")
        assert question2.status == NodeStatus.COMPLETE
        assert orchestrator._data.get("email") == "bob@example.com"
        assert final_node.status == NodeStatus.COMPLETE
        assert orchestrator.is_ended is True

    async def test_mixed_nodes_with_questions(self, orchestrator):
        """Test workflow mixing regular nodes with question nodes."""
        greeting = MockNode("greeting", data={"message": "Hello!"})
        question = QuestionNode("ask_name", "What is your name?", "name")
        farewell = MockNode("farewell", data={"message": "Goodbye!"})

        greeting.next = question
        question.next = farewell

        orchestrator.start(greeting)

        # First process: greeting executes, question asks
        await orchestrator.process()

        assert greeting.status == NodeStatus.COMPLETE
        assert question.status == NodeStatus.AWAITING_INPUT
        assert farewell.execute_count == 0

        # Second process: provide answer, farewell executes
        await orchestrator.process(input="Charlie")

        assert question.status == NodeStatus.COMPLETE
        assert farewell.status == NodeStatus.COMPLETE
        assert orchestrator._data.get("name") == "Charlie"
        assert orchestrator._data.get("message") == "Goodbye!"
        assert orchestrator.is_ended is True

    async def test_question_node_reset_behavior(self, orchestrator):
        """Test that question nodes work correctly after reset."""
        question = QuestionNode("ask_color", "What is your favorite color?", "color")
        orchestrator.start(question)

        # First run: ask question
        await orchestrator.process()
        assert question.status == NodeStatus.AWAITING_INPUT

        # Provide answer
        await orchestrator.process(input="blue")
        assert question.status == NodeStatus.COMPLETE
        assert orchestrator.is_ended is True

        # Reset and try again
        orchestrator.reset()
        question._has_asked = False  # Reset internal state

        await orchestrator.process()
        assert question.status == NodeStatus.AWAITING_INPUT
        assert orchestrator.is_ended is False

    async def test_input_persistence_between_calls(self, orchestrator):
        """Test that input is stored in workflow data."""
        node1 = MockNode("node1")
        node2 = MockNode("node2")
        node1.next = node2

        orchestrator.start(node1)

        # Process with input
        await orchestrator.process(input="test_input")

        # Verify input is in data
        assert orchestrator._data.get("_user_input") == "test_input"
        assert orchestrator.is_ended is True

    async def test_question_validation_edge_cases(self, orchestrator):
        """Test question node validation with edge cases."""

        def validate_not_empty(value: str) -> bool:
            return bool(value and value.strip())

        question = QuestionNode(
            "ask_comment",
            "Leave a comment:",
            "comment",
            validate_func=validate_not_empty,
        )
        orchestrator.start(question)

        # Ask question
        await orchestrator.process()
        assert question.status == NodeStatus.AWAITING_INPUT

        # Provide empty input
        await orchestrator.process(input="")
        assert question.status == NodeStatus.AWAITING_INPUT
        assert orchestrator.is_ended is False

        # Provide whitespace input
        await orchestrator.process(input="   ")
        assert question.status == NodeStatus.AWAITING_INPUT
        assert orchestrator.is_ended is False

        # Provide valid input
        await orchestrator.process(input="Great!")
        assert question.status == NodeStatus.COMPLETE
        assert orchestrator._data.get("comment") == "Great!"
        assert orchestrator.is_ended is True
