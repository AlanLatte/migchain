"""MigChain - Database Migration Management CLI Tool.

Built on top of yoyo-migrations with dependency graph analysis,
phased execution, batch tracking, and domain filtering.

Usage as CLI:
    migchain --dsn postgresql://user:pass@localhost/db --apply

Usage as library:
    from migchain.core.config import MigrationConfig
    from migchain.manager import MigrationManager

    config = MigrationConfig(dsn="postgresql://...", verbose=True)
    manager = MigrationManager(config)
    manager.run("apply")
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from migchain.cli.parser import CLIParser
    from migchain.core import (
        DependencyAnalyzer,
        GraphGenerator,
        MigrationAnalyzer,
        MigrationConfig,
        MigrationPlan,
        MigrationStructure,
    )
    from migchain.manager import MigrationManager
    from migchain.operations import (
        BackendManager,
        MigrationDiscovery,
        MigrationExecutor,
        MigrationPlanner,
    )
    from migchain.reporting import LoggingManager, ReportGenerator

__version__ = "2.0.0"
