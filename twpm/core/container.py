from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


# TODO: Add life cycle scopes like SCOPED for request-based lifetimes.
class ServiceScope(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    # SCOPED = "scoped"


Factory = Callable[[], Any]


@dataclass
class Provider:
    scope: ServiceScope
    default_factory: Factory
    instance: Any = None


class Container:
    def __init__(self) -> None:
        self.providers: dict[Any, Provider] = {}

    def register(self, key: Any, default_factory: Factory, scope: ServiceScope) -> None:
        self.providers[key] = Provider(scope=scope, default_factory=default_factory)

    def resolve(self, key: Any) -> Any:
        p = self.providers[key]

        if p.scope == ServiceScope.SINGLETON:
            if p.instance is None:
                p.instance = p.default_factory()
            return p.instance

        return p.default_factory()
