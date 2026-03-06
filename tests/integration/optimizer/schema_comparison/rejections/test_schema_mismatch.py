"""TestcontainerSchemaComparator.verify -- different schemas are unsafe.

- migrations producing different tables -> is_safe=False
- differences list contains meaningful entries
"""

import pytest

from migchain.infrastructure.schema_comparator import TestcontainerSchemaComparator


@pytest.mark.integration
class TestSchemaMismatch:
    """Protects against false positives when schemas actually differ."""

    def test_different_migrations_are_unsafe(self, tmp_path):
        """Protects against is_safe=True when schemas differ."""
        original = tmp_path / "original" / "domain"
        original.mkdir(parents=True)
        (original / "0001_init.py").write_text(
            "from yoyo import step\n\n"
            "steps = [\n"
            '    step("CREATE TABLE public.test_a '
            '(id serial PRIMARY KEY, name text)"),\n'
            "]\n",
        )

        optimized = tmp_path / "optimized" / "domain"
        optimized.mkdir(parents=True)
        (optimized / "0001_init.py").write_text(
            "from yoyo import step\n\n"
            "steps = [\n"
            '    step("CREATE TABLE public.test_b '
            '(id serial PRIMARY KEY, value int)"),\n'
            "]\n",
        )

        comparator = TestcontainerSchemaComparator()
        result = comparator.verify(
            [original],
            [optimized],
        )

        assert result.is_safe is False
        assert len(result.differences) > 0
