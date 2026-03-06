"""Constants and patterns for migration management."""

import re

DEFAULT_DOMAIN_LEVEL = 0
MIGRATION_FILE_EXTENSION = ".py"
INIT_FILE = "__init__.py"
DEPENDENCY_PATTERN = re.compile(r"<Migration\s+'([^']+)'\b")

LOGGER_NAME = "migchain"
