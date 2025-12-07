import logging
from functools import wraps
from typing import Callable

from twpm.core.base import NodeResult


def safe_execute(logger: logging.Logger | None = None):
    """
    Decorator that ensures execute() methods always return a NodeResult,
    catching any exceptions not handled correctly and converting them to failed results.

    This guarantees predictable behavior and prevents exceptions from
    propagating up to the orchestrator.

    Args:
        logger: Optional logger instance. If not provided, uses module logger.

    Returns:
        Decorated function that guarantees NodeResult return type.

    Example:
        >>> class MyNode(Node):
        ...     @safe_execute()
        ...     async def execute(self, data: ListData) -> NodeResult:
        ...         # This might raise an exception
        ...         risky_operation()
        ...         return NodeResult(success=True, data={}, message="")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(self, *args, **kwargs) -> NodeResult:
            node_logger = logger or logging.getLogger(__name__)
            node_id = getattr(self, "key", self.__class__.__name__)

            try:
                result = await func(self, *args, **kwargs)
                return result
            except Exception as e:
                node_logger.error(
                    f"Exception in node '{node_id}' execute(): {e}", exc_info=True
                )
                return NodeResult(
                    success=False,
                    data={},
                    message=f"Exception in node '{node_id}': {e!s}",
                    is_awaiting_input=False,
                )

        return wrapper

    return decorator
