"""Dependency analysis for migrations."""

from collections import defaultdict, deque
from typing import Any, Dict, List, Set, Tuple

from yoyo.migrations import MigrationList

from migchain.constants import DEPENDENCY_PATTERN


class DependencyAnalyzer:
    """Analyzes migration dependencies and builds dependency graphs."""

    @staticmethod
    def extract_dependency_ids(dependency: Any) -> Set[str]:
        ids: Set[str] = set()

        def _add_id(obj: Any) -> None:
            if hasattr(obj, "id") and isinstance(getattr(obj, "id"), str):
                ids.add(getattr(obj, "id"))
                return

            if isinstance(obj, (list, tuple, set, frozenset)):
                for item in obj:
                    _add_id(item)
                return

            if isinstance(obj, str):
                match = DEPENDENCY_PATTERN.search(obj)
                ids.add(match.group(1) if match else obj)
                return

            string_repr = str(obj)
            match = DEPENDENCY_PATTERN.search(string_repr)
            ids.add(match.group(1) if match else string_repr)

        _add_id(dependency)
        return ids

    @classmethod
    def build_dependency_graph(
        cls, migrations: MigrationList
    ) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        migration_ids = {migration.id for migration in migrations}
        dependencies: Dict[str, Set[str]] = {
            migration.id: set() for migration in migrations
        }
        reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        missing_dependencies: List[Tuple[str, str]] = []

        for migration in migrations:
            migration_deps = cls.extract_dependency_ids(
                getattr(migration, "depends", None)
            )

            for dep_id in migration_deps:
                if dep_id not in migration_ids:
                    missing_dependencies.append((migration.id, dep_id))
                else:
                    dependencies[migration.id].add(dep_id)
                    reverse_dependencies[dep_id].add(migration.id)

        if missing_dependencies:
            error_details = "\n".join(
                [
                    f"  - {mid} depends on missing {dep}"
                    for mid, dep in missing_dependencies
                ]
            )
            raise SystemExit(f"[graph] Missing dependency IDs:\n{error_details}")

        return dependencies, reverse_dependencies

    @staticmethod
    def topological_sort(dependencies: Dict[str, Set[str]]) -> List[str]:
        in_degree = {node: len(deps) for node, deps in dependencies.items()}
        reverse_deps = defaultdict(set)

        for child, parents in dependencies.items():
            for parent in parents:
                reverse_deps[parent].add(child)

        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        sorted_order: List[str] = []

        while queue:
            current_node = queue.popleft()
            sorted_order.append(current_node)

            for child in reverse_deps[current_node]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(sorted_order) != len(dependencies):
            cyclic_nodes = [node for node, degree in in_degree.items() if degree > 0]
            error_details = "\n".join(
                [
                    f"  - {node}: in_degree={in_degree[node]}, "
                    f"depends={sorted(dependencies[node])}"
                    for node in cyclic_nodes
                ]
            )
            raise SystemExit(
                f"[graph] Cycle detected in migration dependencies:\n{error_details}"
            )

        return sorted_order
