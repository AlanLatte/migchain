"""Port interfaces (driven adapters)."""

from contextlib import AbstractContextManager
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Protocol, Sequence, Set, Tuple

from migchain.domain.models import (
    MigrationPlan,
    MigrationStructure,
    OptimizationResult,
    OptimizationVerification,
)
from migchain.domain.scaffolder import ScaffoldRequest


class MigrationRepository(Protocol):
    """Port for discovering and reading migration files."""

    def discover_directories(
        self,
        root: Path,
        include_domains: Optional[Set[str]] = None,
        exclude_domains: Optional[Set[str]] = None,
        domain_level: int = 0,
    ) -> List[Path]: ...

    def read_migrations(self, paths: Sequence[Path]) -> Any: ...


class MigrationBackend(Protocol):
    """Port for database migration operations."""

    @property
    def connection(self) -> Any: ...

    def connect(
        self,
        dsn: str,
        testing: bool = False,
        database_name_override: Optional[str] = None,
    ) -> None: ...

    def pending(self, migrations: Any) -> List[Any]: ...

    def applied(self, migrations: Any) -> List[Any]: ...

    def apply_one(self, migration: Any) -> None: ...

    def rollback_one(self, migration: Any) -> None: ...

    def acquire_lock(self) -> AbstractContextManager[Any]: ...


class BatchStorage(Protocol):
    """Port for migration batch tracking."""

    def ensure_ready(self, connection: Any) -> None: ...

    def next_batch_number(self, connection: Any) -> int: ...

    def record_apply(
        self,
        connection: Any,
        batch: int,
        ids: List[str],
    ) -> None: ...

    def record_rollback(
        self,
        connection: Any,
        batch: int,
        ids: List[str],
    ) -> None: ...

    def latest_batch(
        self,
        connection: Any,
    ) -> Optional[Tuple[int, List[str]]]: ...


class Presenter(Protocol):
    """Port for user interface output."""

    def setup(self, verbosity: int) -> None: ...

    # ::::: Structure & Plan :::::
    def show_structure(self, structure: MigrationStructure) -> None: ...

    def show_plan(
        self,
        plan: MigrationPlan,
        mode: str,
        migrations_root: Optional[Path] = None,
    ) -> None: ...

    def show_graph(self, content: str) -> None: ...

    # ::::: Result :::::
    def show_result(self, message: str) -> None: ...

    # ::::: Execution lifecycle :::::
    def start_execution(self, total: int, tag: str) -> None: ...

    def on_migration_start(self, migration_id: str, tag: str) -> None: ...

    def on_migration_success(
        self,
        migration_id: str,
        tag: str,
        duration: float,
    ) -> None: ...

    def on_migration_fail(self, migration_id: str, tag: str) -> None: ...

    def finish_execution(self) -> None: ...

    # ::::: Interactive :::::
    def confirm(self, message: str) -> bool: ...

    # ::::: Logging :::::
    def info(self, message: str) -> None: ...

    def warning(self, message: str) -> None: ...

    def error(self, message: str) -> None: ...

    def debug(self, message: str) -> None: ...

    # ::::: Optimization :::::
    def show_redundant_edges(self, result: OptimizationResult) -> None: ...

    def show_verification_result(
        self,
        verification: OptimizationVerification,
    ) -> None: ...

    # ::::: Scaffolding :::::
    def prompt_scaffold(
        self,
        existing_domains: List[str],
        domain_subdirectories: Mapping[str, List[str]],
    ) -> ScaffoldRequest: ...


class SchemaComparator(Protocol):
    """Port for verifying optimization safety via ephemeral databases."""

    def verify(
        self,
        original_paths: Sequence[Path],
        optimized_paths: Sequence[Path],
    ) -> OptimizationVerification: ...


class MigrationFileWriter(Protocol):
    """Port for modifying migration file dependencies."""

    def prepare_temp_copies(
        self,
        migrations_root: Path,
        optimized_dependencies: Dict[str, Set[str]],
        migration_id_to_path: Dict[str, Path],
    ) -> Path: ...

    def apply_to_source(
        self,
        migration_id_to_path: Dict[str, Path],
        optimized_dependencies: Dict[str, Set[str]],
    ) -> List[str]: ...
