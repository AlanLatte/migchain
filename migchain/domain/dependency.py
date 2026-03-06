"""Domain service: dependency graph analysis."""

from collections import defaultdict, deque
from typing import Any, Dict, List, Set, Tuple

from migchain.constants import DEPENDENCY_PATTERN


class DependencyResolver:
    """Pure domain logic for migration dependency analysis."""

    @staticmethod
    def extract_dependency_ids(dependency: Any) -> Set[str]:
        ids: Set[str] = set()

        def _collect(obj: Any) -> None:
            if hasattr(obj, "id") and isinstance(getattr(obj, "id"), str):
                ids.add(getattr(obj, "id"))
                return

            if isinstance(obj, (list, tuple, set, frozenset)):
                for item in obj:
                    _collect(item)
                return

            if isinstance(obj, str):
                match = DEPENDENCY_PATTERN.search(obj)
                ids.add(match.group(1) if match else obj)
                return

            string_repr = str(obj)
            match = DEPENDENCY_PATTERN.search(string_repr)
            ids.add(match.group(1) if match else string_repr)

        _collect(dependency)
        return ids

    @classmethod
    def build_graph(
        cls,
        migrations: Any,
    ) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]:
        migration_ids = {m.id for m in migrations}
        deps: Dict[str, Set[str]] = {m.id: set() for m in migrations}
        reverse: Dict[str, Set[str]] = defaultdict(set)
        missing: List[Tuple[str, str]] = []

        for migration in migrations:
            extracted = cls.extract_dependency_ids(
                getattr(migration, "depends", None),
            )
            for dep_id in extracted:
                if dep_id not in migration_ids:
                    missing.append((migration.id, dep_id))
                else:
                    deps[migration.id].add(dep_id)
                    reverse[dep_id].add(migration.id)

        if missing:
            details = "\n".join(
                f"  - {mid} depends on missing {dep}" for mid, dep in missing
            )
            raise SystemExit(f"[graph] Missing dependency IDs:\n{details}")

        return deps, reverse

    @staticmethod
    def topological_sort(dependencies: Dict[str, Set[str]]) -> List[str]:
        in_degree = {node: len(deps) for node, deps in dependencies.items()}
        reverse = defaultdict(set)

        for child, parents in dependencies.items():
            for parent in parents:
                reverse[parent].add(child)

        queue = deque(node for node, degree in in_degree.items() if degree == 0)
        ordered: List[str] = []

        while queue:
            current = queue.popleft()
            ordered.append(current)
            for child in reverse[current]:
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        if len(ordered) != len(dependencies):
            cyclic = [n for n, d in in_degree.items() if d > 0]
            details = "\n".join(
                f"  - {n}: in_degree={in_degree[n]}, depends={sorted(dependencies[n])}"
                for n in cyclic
            )
            raise SystemExit(
                f"[graph] Cycle detected:\n{details}",
            )

        return ordered
