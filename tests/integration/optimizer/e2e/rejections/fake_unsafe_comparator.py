"""Fake comparator that always reports schema mismatch."""

from pathlib import Path
from typing import Sequence

from migchain.domain.models import OptimizationVerification, SchemaSnapshot


class FakeUnsafeComparator:
    """SchemaComparator that simulates schema mismatch."""

    def verify(
        self,
        _original_paths: Sequence[Path],
        _optimized_paths: Sequence[Path],
    ) -> OptimizationVerification:
        return OptimizationVerification(
            is_safe=False,
            differences=["[tables] missing in optimized: users"],
            original_snapshot=SchemaSnapshot(),
            optimized_snapshot=SchemaSnapshot(),
        )
