"""Entry point — composition root wiring all adapters."""

from migchain.application.service import MigrationService
from migchain.domain.ports import Presenter
from migchain.infrastructure.batch_tracker import PostgresBatchTracker
from migchain.infrastructure.migration_writer import FilesystemMigrationWriter
from migchain.infrastructure.yoyo_backend import YoyoBackendAdapter
from migchain.infrastructure.yoyo_discovery import YoyoDiscoveryAdapter
from migchain.presentation.cli import build_config, create_parser, resolve_operation
from migchain.presentation.plain import PlainPresenter

try:
    from migchain.infrastructure.schema_comparator import (
        TestcontainerSchemaComparator,
    )
    from migchain.presentation.console import RichPresenter

    _HAS_FULL_DEPS = True
except ImportError:
    _HAS_FULL_DEPS = False


def _create_presenter() -> Presenter:
    """Select presenter based on available dependencies."""
    if _HAS_FULL_DEPS:
        return RichPresenter()
    return PlainPresenter()


def main() -> None:
    """Wire adapters and run the migration service."""
    parser = create_parser()
    args = parser.parse_args()

    operation = resolve_operation(args)
    config = build_config(args)
    presenter = _create_presenter()

    schema_comparator = None
    migration_writer = None

    if operation == "optimize":
        if not _HAS_FULL_DEPS:
            raise SystemExit(
                "The --optimize feature requires extra dependencies.\n"
                "Install with: uv add migchain[full]",
            )
        schema_comparator = TestcontainerSchemaComparator()
        migration_writer = FilesystemMigrationWriter()

    service = MigrationService(
        config=config,
        repository=YoyoDiscoveryAdapter(),
        backend=YoyoBackendAdapter(),
        batch_storage=PostgresBatchTracker(),
        presenter=presenter,
        schema_comparator=schema_comparator,
        migration_writer=migration_writer,
    )

    service.run(operation)


if __name__ == "__main__":
    main()
