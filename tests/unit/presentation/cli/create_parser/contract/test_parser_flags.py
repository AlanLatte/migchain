"""create_parser -- argument parser structure and defaults.

- prog name is "migchain"
- --migrations-dir defaults to "./migrations"
- --dsn accepts connection string
- --apply, --rollback flags work
- --apply and --rollback are mutually exclusive
- --dry-run flag
- -vv increments verbose count
- --include accepts comma string
- --gw-count accepts integer
- -q/--quiet flag
"""

import pytest

from migchain.presentation.cli import create_parser


class TestParserFlags:
    """Protects the contract of CLI argument parser structure and default values."""

    def test_returns_parser(self):
        """Protects against wrong program name in parser configuration."""
        parser = create_parser()
        assert parser.prog == "migchain"

    def test_default_migrations_dir(self):
        """Protects against incorrect default for --migrations-dir."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.migrations_dir == "./migrations"

    def test_dsn_flag(self):
        """Protects against --dsn not accepting a connection string."""
        parser = create_parser()
        args = parser.parse_args(["--dsn", "postgresql://localhost/db"])
        assert args.dsn == "postgresql://localhost/db"

    def test_apply_flag(self):
        """Protects against --apply not setting the flag to True."""
        parser = create_parser()
        args = parser.parse_args(["--apply"])
        assert args.apply is True

    def test_rollback_flag(self):
        """Protects against --rollback not setting the flag to True."""
        parser = create_parser()
        args = parser.parse_args(["--rollback"])
        assert args.rollback is True

    def test_mutually_exclusive_operations(self):
        """Protects against --apply and --rollback being used simultaneously."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--apply", "--rollback"])

    def test_dry_run_flag(self):
        """Protects against --dry-run not setting the flag to True."""
        parser = create_parser()
        args = parser.parse_args(["--dry-run"])
        assert args.dry_run is True

    def test_verbose_increments(self):
        """Protects against -vv not incrementing verbose count correctly."""
        parser = create_parser()
        args = parser.parse_args(["-vv"])
        assert args.verbose == 3

    def test_include_flag(self):
        """Protects against --include not accepting a comma-separated string."""
        parser = create_parser()
        args = parser.parse_args(["--include", "auth,billing"])
        assert args.include == "auth,billing"

    def test_gw_count(self):
        """Protects against --gw-count not accepting an integer value."""
        parser = create_parser()
        args = parser.parse_args(["--gw-count", "3"])
        assert args.gw_count == 3

    def test_quiet_flag(self):
        """Protects against -q/--quiet not setting the flag to True."""
        parser = create_parser()
        args = parser.parse_args(["-q"])
        assert args.quiet is True
