"""Application configuration."""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Set

from migchain.constants import DEFAULT_DOMAIN_LEVEL


@dataclass
class MigrationConfig:
    """Configuration for migration operations."""

    dsn: str = ""
    migrations_root: Path = field(default_factory=lambda: Path("./migrations"))
    include_domains: Optional[Set[str]] = None
    exclude_domains: Optional[Set[str]] = None
    domain_level: int = DEFAULT_DOMAIN_LEVEL
    run_inserters: bool = True
    dry_run: bool = False
    testing: bool = False
    verbose: bool = False
    auto_confirm: bool = False
    show_structure: bool = False
    show_graph: bool = False
    graph_output_file: Optional[str] = None
    json_plan_output_file: Optional[str] = None
    gw_count: Optional[int] = None
    gw_template: Optional[str] = None


def extract_database_name(dsn: str) -> str:
    """Extract database name from a PostgreSQL DSN."""
    match = re.search(r"/([\w-]+)(\?|$)", dsn)
    if match:
        return match.group(1)
    raise ValueError("Cannot extract database name from DSN")
