"""Domain entities and value objects."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


@dataclass
class DomainStats:
    """Per-domain migration statistics."""

    schema_count: int = 0
    inserter_count: int = 0
    migration_ids: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.schema_count + self.inserter_count


@dataclass
class MigrationStructure:
    """Analysis of migration structure."""

    total: int = 0
    schema_count: int = 0
    inserter_count: int = 0
    domains: Dict[str, DomainStats] = field(default_factory=dict)
    schema_paths: Set[str] = field(default_factory=set)
    inserter_paths: Set[str] = field(default_factory=set)


@dataclass
class MigrationPlan:
    """Execution plan with categorized migrations."""

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


# ::::: Optimization :::::


@dataclass
class RedundantEdge:
    """A dependency edge removable via transitive reduction."""

    child_id: str
    parent_id: str
    path: List[str] = field(default_factory=list)


@dataclass
class OptimizationResult:
    """Result of dependency graph optimization analysis."""

    original_edge_count: int
    reduced_edge_count: int
    redundant_edges: List[RedundantEdge] = field(default_factory=list)
    reduced_dependencies: Dict[str, Set[str]] = field(default_factory=dict)


@dataclass
class SchemaSnapshot:
    """Normalized database schema for comparison."""

    tables: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    indexes: Dict[str, str] = field(default_factory=dict)
    constraints: Dict[str, str] = field(default_factory=dict)

    def as_comparable(self) -> Dict[str, Any]:
        """Return a deterministically sorted representation."""
        return {
            "tables": {
                k: sorted(v, key=lambda c: c.get("column_name", ""))
                for k, v in sorted(self.tables.items())
            },
            "indexes": dict(sorted(self.indexes.items())),
            "constraints": dict(sorted(self.constraints.items())),
        }


@dataclass
class OptimizationVerification:
    """Result of schema comparison between original and optimized migrations."""

    is_safe: bool
    differences: List[str] = field(default_factory=list)
    original_snapshot: Optional[SchemaSnapshot] = None
    optimized_snapshot: Optional[SchemaSnapshot] = None
