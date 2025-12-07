import inspect
import logging
from enum import Enum, auto
from typing import Any

from twpm.core.base import ListData, Node, NodeResult, NodeStatus
from twpm.core.container import Container
from twpm.core.depedencies import Output

logger = logging.getLogger(__name__)


class OrchestratorState(Enum):
    DEFAULT = auto()
    STARTED = auto()
    FINISHED = auto()
    ERROR = auto()


class Orchestrator:
    def __init__(
        self, container: Container, logger: logging.Logger | None = None
    ) -> None:
        self._head: Node | None = None
        self._current: Node | None = None
        self._data: ListData = ListData(data={})
        self._state: OrchestratorState = OrchestratorState.DEFAULT

        self._session_id: str | None = None

        self.container = container
        self.logger = logger or logging.getLogger(__name__)

    @property
    def is_finished(self) -> bool:
        return self._state == OrchestratorState.FINISHED

    @property
    def is_started(self) -> bool:
        return self._state == OrchestratorState.STARTED

    @property
    def current_node(self) -> Node | None:
        """Get the current node being processed."""
        return self._current

    @property
    def session_id(self) -> str | None:
        return self._session_id

    def start(self, session_id: str, start_node: Node):
        """Initialize and start the orchestrator with a starting node."""
        self._state = OrchestratorState.STARTED
        self._session_id = session_id
        self._head = start_node
        self._current = start_node
        self.logger.info(
            f"Orchestrator started with node: {self._get_node_identifier(start_node)}"
        )

    def reset(self):
        """Reset the orchestrator to the beginning of the workflow."""
        self._state = OrchestratorState.DEFAULT
        self._current = self._head
        self.logger.info("Orchestrator reset to head node")

    def inject(self, node: Node) -> dict[str, Any]:
        """
        Build dependency injection kwargs for node execution.

        Returns:
            Dictionary of parameter names to injected values
        """
        execute_method = node.execute
        func_signature = inspect.signature(execute_method)
        kwargs: dict[str, Any] = {}

        kwargs["data"] = self._data

        if "output" in func_signature.parameters:
            kwargs["output"] = self.container.resolve(Output)

        return kwargs

    async def process(self, input: str | None = None):
        """
        Main processing loop that executes nodes sequentially.
        Continues until workflow ends or awaits input.

        Args:
            input: Optional input string to provide to nodes (e.g., user response)

        Note: Exceptions in nodes are handled by the @safe_execute decorator,
        so this method will never receive exceptions from node.execute().
        """
        if not self.is_started:
            self.logger.error("Cannot process: orchestrator not started")
            raise RuntimeError("Orchestrator must be started before processing")

        self.logger.info("Starting process execution")

        if input is not None:
            self._data["_user_input"] = input
            self.logger.debug(f"User input received: {input}")

        while self._current is not None:
            node_id = self._get_node_identifier(self._current)

            result = await self._execute_node(self._current)

            if not self._handle_node_result(result, node_id):
                return

        self._end_workflow("All nodes processed successfully")

    async def _execute_node(self, node: Node) -> NodeResult:
        """Execute a single node and update its status."""
        node_id = self._get_node_identifier(node)

        self.logger.debug(f"Executing node: {node_id}")
        node.status = NodeStatus.DEFAULT

        kwargs = self.inject(node)
        result = await node.execute(**kwargs)

        self.logger.debug(
            f"Node {node_id} execution completed - Success: {result.success}"
        )

        return result

    def _handle_node_result(self, result: NodeResult, node_id: str) -> bool:
        """
        Handle the result of a node execution.
        Returns True to continue processing, False to stop.
        """
        assert self._current is not None, "Current is None"

        if result.is_awaiting_input:
            self.logger.info(f"Node {node_id} is awaiting input: {result.message}")
            self._current.status = NodeStatus.AWAITING_INPUT
            if result.data:
                self._merge_result_data(result.data)
                self.logger.debug(f"Merged data from node {node_id}: {result.data}")
            return False

        if not result.success:
            self.logger.warning(f"Node {node_id} failed: {result.message}")
            self._current.status = NodeStatus.FAILED
            self._end_workflow(f"Node {node_id} failed")
            return False

        if result.data:
            self._merge_result_data(result.data)
            self.logger.debug(f"Merged data from node {node_id}: {result.data}")

        self._current.status = NodeStatus.COMPLETE
        self._current = self._current.next

        if self._current:
            next_id = self._get_node_identifier(self._current)
            self.logger.debug(f"Moving to next node: {next_id}")

        return True

    def _merge_result_data(self, result_data: dict[str, str]) -> None:
        """Merge result data into the workflow's shared data."""
        self._data.update(result_data)

    def _end_workflow(self, reason: str) -> None:
        """Mark the workflow as ended and log the reason."""
        self._state = OrchestratorState.FINISHED
        self.logger.info(f"Workflow ended: {reason}")

    def _get_node_identifier(self, node: Node) -> str:
        """Get a readable identifier for a node."""
        if hasattr(node, "key") and node.key:
            return node.key
        return f"{node.__class__.__name__}@{id(node)}"
