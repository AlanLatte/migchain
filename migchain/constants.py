"""Constants and patterns for migration management."""

import re

DEFAULT_DOMAIN_LEVEL = 0
MIGRATION_FILE_EXTENSION = ".py"
INIT_FILE = "__init__.py"
DEPENDENCY_PATTERN = re.compile(r"<Migration\s+'([^']+)'\b")
LOGGER_NAME = "migchain"

CONFIRM_MESSAGES = {
    "rollback": "This will rollback ALL applied migrations. Continue?",
    "rollback-latest": "This will rollback the latest applied batch. Continue?",
    "reload": "This will rollback ALL and reapply ALL migrations. Continue?",
}
