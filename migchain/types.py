"""Type protocols and aliases for migration management."""

from contextlib import AbstractContextManager
from typing import Any, Iterable, Protocol


class YoyoBackend(Protocol):
    """Protocol for yoyo backend interface."""

    def lock(self) -> AbstractContextManager[Any]:
        ...

    def apply_migrations(self, migrations: Iterable[Any]) -> None:
        ...

    def rollback_migrations(self, migrations: Iterable[Any]) -> None:
        ...

    def to_apply(self, migrations: Iterable[Any]) -> Iterable[Any]:
        ...

    def to_rollback(self, migrations: Iterable[Any]) -> Iterable[Any]:
        ...
