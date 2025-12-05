from typing import Protocol


class Output(Protocol):
    def send_text(self, message: str) -> None: ...
