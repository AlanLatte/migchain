"""resolve_operation -- maps argparse flags to operation mode strings.

- apply flag -> "apply"
- rollback flag -> "rollback"
- rollback_one flag -> "rollback-one"
- rollback_latest flag -> "rollback-latest"
- reload flag -> "reload"
- optimize flag -> "optimize"
"""

from migchain.presentation.cli import resolve_operation


class TestMapsFlagsToModes:
    """Protects the contract of mapping namespace flags to operation mode strings."""

    def test_apply(self, base_namespace):
        """Protects against apply flag not resolving to 'apply' mode."""
        base_namespace.apply = True
        assert resolve_operation(base_namespace) == "apply"

    def test_rollback(self, base_namespace):
        """Protects against rollback flag not resolving to 'rollback' mode."""
        base_namespace.rollback = True
        assert resolve_operation(base_namespace) == "rollback"

    def test_rollback_one(self, base_namespace):
        """Protects against rollback_one flag not resolving to 'rollback-one' mode."""
        base_namespace.rollback_one = True
        assert resolve_operation(base_namespace) == "rollback-one"

    def test_rollback_latest(self, base_namespace):
        """Protects against rollback_latest flag not resolving
        to 'rollback-latest' mode."""
        base_namespace.rollback_latest = True
        assert resolve_operation(base_namespace) == "rollback-latest"

    def test_reload(self, base_namespace):
        """Protects against reload flag not resolving to 'reload' mode."""
        base_namespace.reload = True
        assert resolve_operation(base_namespace) == "reload"

    def test_optimize(self, base_namespace):
        """Protects against optimize flag not resolving to 'optimize' mode."""
        base_namespace.optimize = True
        assert resolve_operation(base_namespace) == "optimize"
