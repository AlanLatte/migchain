"""Entry point for running migchain as a module or CLI."""

from migchain.cli.parser import CLIParser
from migchain.manager import MigrationManager


def main() -> None:
    """Main entry point for the migration tool."""
    parser = CLIParser.create_parser()
    args = parser.parse_args()

    config = CLIParser.parse_config(args)
    operation_mode = CLIParser.determine_operation_mode(args)

    manager = MigrationManager(config)
    manager.run(operation_mode)


if __name__ == "__main__":
    main()
