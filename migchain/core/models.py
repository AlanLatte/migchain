"""Data models for migration management."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Set


@dataclass
class MigrationPlan:
    """Plan for migration execution."""

    schema_migrations: List[Any] = field(default_factory=list)
    inserter_migrations: List[Any] = field(default_factory=list)
    all_migrations: List[Any] = field(default_factory=list)

    @property
    def total_count(self) -> int:
        return len(self.all_migrations)

    @property
    def schema_count(self) -> int:
        return len(self.schema_migrations)

    @property
    def inserter_count(self) -> int:
        return len(self.inserter_migrations)


@dataclass
class MigrationStructure:
    """Analysis of migration structure."""

    total: int = 0
    by_category: Dict[str, int] = field(default_factory=dict)
    by_domain: Dict[str, List[str]] = field(default_factory=dict)
    by_path: Dict[str, List[str]] = field(default_factory=dict)
    inserter_paths: Set[str] = field(default_factory=set)
    schema_paths: Set[str] = field(default_factory=set)
