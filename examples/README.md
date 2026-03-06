# MigChain Examples

## Directory structure

```
migrations/
├── auth/
│   ├── users/
│   │   └── 20250101_01_create_users.py
│   └── roles/
│       └── 20250101_02_create_roles.py
└── billing/
    ├── plans/
    │   ├── 20250102_01_create_plans.py
    │   └── inserters/
    │       └── 20250102_03_seed_plans.py
    └── subscriptions/
        └── 20250102_02_create_subscriptions.py
```

- Each **domain** (`auth`, `billing`) is a top-level directory
- Each **table** gets its own subdirectory (`users/`, `plans/`, ...)
- **Inserters** (seed data) live in `inserters/` nested under the table they belong to
- Cross-domain dependencies work via `__depends__` referencing migration IDs

## Usage

```bash
# Apply all migrations
migchain --dsn postgresql://user:pass@localhost/mydb \
         --migrations-dir ./migrations \
         --apply

# Dry run — see the execution plan
migchain --dsn postgresql://user:pass@localhost/mydb \
         --migrations-dir ./migrations \
         --dry-run -vv

# Apply only auth domain
migchain --dsn postgresql://user:pass@localhost/mydb \
         --migrations-dir ./migrations \
         --include auth --apply

# Apply schema only, skip inserters
migchain --dsn postgresql://user:pass@localhost/mydb \
         --migrations-dir ./migrations \
         --no-inserters --apply

# Rollback latest batch
migchain --dsn postgresql://user:pass@localhost/mydb \
         --migrations-dir ./migrations \
         --rollback-latest

# Export dependency graph as Mermaid
migchain --dsn postgresql://user:pass@localhost/mydb \
         --migrations-dir ./migrations \
         --show-graph --graph-out deps.mmd

# Domain filtering uses directory level
# Level 0 (default): auth, billing
# Level 1: users, roles, plans, subscriptions
migchain --migrations-dir ./migrations \
         --domain-level 1 --include plans --dry-run
```
