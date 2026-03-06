"""Domain service: dependency graph optimization via transitive reduction."""

from collections import deque
from typing import Dict, List, Set

from migchain.domain.models import OptimizationResult, RedundantEdge


class GraphOptimizer:
    """Pure domain logic for removing redundant dependency edges."""

    @staticmethod
    def transitive_reduction(
        dependencies: Dict[str, Set[str]],
    ) -> OptimizationResult:
        """Compute transitive reduction and identify all redundant edges."""
        original_count = sum(len(deps) for deps in dependencies.values())
        redundant: List[RedundantEdge] = []

        for child, parents in dependencies.items():
            for parent in list(parents):
                path = GraphOptimizer._find_alternative_path(
                    dependencies,
                    child,
                    parent,
                )
                if path:
                    redundant.append(
                        RedundantEdge(
                            child_id=child,
                            parent_id=parent,
                            path=path,
                        ),
                    )

        redundant_set = {(e.child_id, e.parent_id) for e in redundant}
        reduced = {
            child: {p for p in parents if (child, p) not in redundant_set}
            for child, parents in dependencies.items()
        }

        return OptimizationResult(
            original_edge_count=original_count,
            reduced_edge_count=original_count - len(redundant),
            redundant_edges=redundant,
            reduced_dependencies=reduced,
        )

    @staticmethod
    def _find_alternative_path(
        dependencies: Dict[str, Set[str]],
        child: str,
        target_parent: str,
    ) -> List[str]:
        """BFS for a path from child to target_parent bypassing the direct edge."""
        other_parents = dependencies.get(child, set()) - {target_parent}
        if not other_parents:
            return []

        visited: Set[str] = set()
        queue: deque[tuple[str, List[str]]] = deque()

        for p in other_parents:
            queue.append((p, [child, p]))

        while queue:
            node, path = queue.popleft()
            if node == target_parent:
                return path

            if node in visited:
                continue
            visited.add(node)

            for ancestor in dependencies.get(node, set()):
                queue.append((ancestor, [*path, ancestor]))

        return []
