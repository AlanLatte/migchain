<div align="center">

# MigChain

**Smart migration orchestrator for PostgreSQL built on top of [yoyo-migrations](https://ollycope.com/software/yoyo/latest/)**



*Dependency graph analysis, batch tracking, phased execution, and dependency optimization — everything yoyo doesn't do.*

</div>

---

## Why MigChain?

yoyo-migrations is great for writing and running individual migrations. But as your project grows to dozens of domains and hundreds of migrations, you hit its limits:

| Problem | yoyo | MigChain |
|---------|------|----------|
| **Cross-domain dependencies** | Flat directory, manual ordering | Domain-based tree structure with `__depends__` |
| **"What will run?"** | Run it and see | `--dry-run` with execution plan and JSON export |
| **Rollback last deploy** | Roll back one by one | `--rollback-latest` undoes the entire batch |
| **Dependency cycles** | Silent failures | Cycle detection with clear error messages |
| **Visualize the graph** | Nothing | Mermaid diagram with domain grouping |
| **Schema vs seed data** | No distinction | Separate schema/inserter phases, `--no-inserters` |
| **Redundant dependencies** | Accumulate forever | `--optimize` with transitive reduction + schema verification |
| **Domain filtering** | Not possible | `--include auth,billing` / `--exclude legacy` |
| **Rich terminal output** | Plain text | Optional Rich UI with progress bars and colored tables |

MigChain wraps yoyo — your existing migrations work as-is. No rewrite needed.

## Quick Start

```bash
pip install migchain

# or with rich terminal UI + optimizer
pip install migchain[full]
```

```bash
export DATABASE_URL=postgresql://user:pass@localhost/mydb

# Apply all pending migrations
migchain --apply

# See what will run without executing
migchain --dry-run -vv

# Rollback last deploy
migchain --rollback-latest

# Visualize dependency graph
migchain --show-graph --graph-out deps.mmd
```

## Migration Structure

MigChain expects migrations organized by domain. Each domain is a top-level directory:

```
migrations/
├── auth/
│   ├── 20250101_00_create_schema.py        # schema creation
│   ├── users/
│   │   └── 20250101_01_create_users.py     # table migration
│   ├── roles/
│   │   └── 20250101_02_create_roles.py     # depends on users
│   └── permissions/
│       └── 20250103_01_create_permissions.py
├── billing/
│   ├── 20250102_00_create_schema.py
│   ├── plans/
│   │   ├── 20250102_01_create_plans.py
│   │   └── inserters/                       # seed data lives here
│   │       └── 20250102_03_seed_plans.py
│   └── subscriptions/
│       └── 20250102_02_create_subscriptions.py  # cross-domain dep on auth.users
├── notifications/
│   └── ...
└── analytics/
    └── ...
```

A migration file is a standard yoyo migration with optional cross-domain dependencies:

```python
"""Create subscriptions table with cross-domain dependency on auth.users."""

from yoyo import step

__depends__ = {
    "20250102_01_create_plans",      # same domain
    "20250101_01_create_users",      # from auth domain
}

steps = [
    step(
        """
        create table if not exists billing.subscriptions (
            id serial primary key,
            user_id integer not null references auth.users(id),
            plan_id integer not null references billing.plans(id),
            status varchar(20) not null default 'active'
        )
        """,
        "drop table if exists billing.subscriptions",
    ),
]
```

Inserter migrations (seed data) live in `inserters/` subdirectories and can be skipped with `--no-inserters`.

## Dependency Graph

MigChain generates Mermaid diagrams showing the full dependency graph grouped by domain:

```bash
migchain --show-graph --graph-out deps.mmd
```

```mermaid
graph TD
  subgraph SG1 [auth]
    20250101_00_create_schema["20250101<br/>00<br/>create<br/>schema"]
    20250101_01_create_users["20250101<br/>01<br/>create<br/>users"]
    20250101_02_create_roles["20250101<br/>02<br/>create<br/>roles"]
  end
  subgraph SG2 [billing]
    20250102_00_create_schema["20250102<br/>00<br/>create<br/>schema"]
    20250102_01_create_plans["20250102<br/>01<br/>create<br/>plans"]
    20250102_02_create_subscriptions["20250102<br/>02<br/>create<br/>subscriptions"]
    20250102_03_seed_plans["20250102<br/>03<br/>seed<br/>plans"]:::inserterNode
  end

  20250101_00_create_schema --> 20250101_01_create_users
  20250101_01_create_users --> 20250101_02_create_roles
  20250102_00_create_schema --> 20250102_01_create_plans
  20250102_01_create_plans --> 20250102_02_create_subscriptions
  20250101_01_create_users --> 20250102_02_create_subscriptions
  20250102_01_create_plans --> 20250102_03_seed_plans

  classDef inserterNode fill:#e1f5fe,stroke:#01579b,stroke-width:2px
  classDef schemaNode fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
  class 20250101_00_create_schema,20250101_01_create_users,20250101_02_create_roles,20250102_00_create_schema,20250102_01_create_plans,20250102_02_create_subscriptions schemaNode
```

- **Purple** nodes = schema migrations (tables, indexes, constraints)
- **Blue** nodes = inserter migrations (seed data)
- Arrows show dependency direction (parent -> child)

## Dependency Optimizer

Over time, migration graphs accumulate redundant edges. MigChain can detect and remove them:

```bash
migchain --optimize
```

If migration C depends on both A and B, and B already depends on A, then C -> A is redundant.
The optimizer uses **transitive reduction** to find these edges, then spins up a PostgreSQL
container via [testcontainers](https://testcontainers-python.readthedocs.io/) to verify
that the optimized graph produces an identical schema.

```
Redundant Dependencies
  #  Migration              Redundant Dep          Alternative Path
  1  create_subscriptions   create_schema          create_schema -> create_plans -> create_subscriptions

Total edges: 15 -> 12
```

Requires `migchain[full]` for testcontainers support.

## Batch Tracking

Every `--apply` groups migrations into a numbered batch. This enables `--rollback-latest` — undo
exactly the migrations from your last deploy, not one at a time.

```
Batch 1: create_schema, create_users, create_roles        (initial deploy)
Batch 2: create_plans, create_subscriptions, seed_plans    (billing feature)
Batch 3: create_events, seed_templates                     (notifications)
```

```bash
# Oops, rollback the notifications deploy
migchain --rollback-latest
# Only batch 3 is rolled back. Batches 1 and 2 stay intact.
```

Batch data is stored in `public._yoyo_migration_batches` alongside yoyo's own tables.

## CLI Reference

### Connection

| Flag | Env Var | Default | Description |
|------|---------|---------|-------------|
| `--dsn` | `DATABASE_URL` | — | PostgreSQL connection string |
| `--migrations-dir` | — | `./migrations` | Path to migrations root |

### Operations

| Flag | Description |
|------|-------------|
| `--apply` | Apply pending migrations (default) |
| `--rollback` | Rollback all applied migrations |
| `--rollback-one` | Rollback one safest leaf migration |
| `--rollback-latest` | Rollback latest batch |
| `--reload` | Rollback all, then reapply all |
| `--optimize` | Optimize dependency graph (requires `[full]`) |
| `--dry-run` | Show execution plan without applying |

### Filtering

| Flag | Description |
|------|-------------|
| `--include DOMAINS` | Only include these domains (comma-separated) |
| `--exclude DOMAINS` | Exclude these domains (comma-separated) |
| `--no-inserters` | Skip seed/inserter migrations |
| `--domain-level N` | Directory nesting level for domain names (default: 0) |

### Output

| Flag | Description |
|------|-------------|
| `--show-structure` | Show migration structure table |
| `--show-graph` | Print Mermaid dependency graph |
| `--graph-out FILE` | Write Mermaid graph to file |
| `--json-plan-out FILE` | Export execution plan as JSON |
| `-v` / `-vv` | Increase verbosity |
| `-q` | Quiet mode (warnings only) |
| `-y` | Skip confirmation prompts |

### Testing

| Flag | Description |
|------|-------------|
| `--testing` | Use test database mode |
| `--gw-count N` | Number of gateway test databases |
| `--gw-template TPL` | Gateway database name template |

## Installation

**Minimal** — CLI with plain text output:
```bash
pip install migchain
```

**Full** — Rich UI, interactive mode, dependency optimizer:
```bash
pip install migchain[full]
```

| Dependency | Included in | Purpose |
|------------|-------------|---------|
| `yoyo-migrations` | base | Migration execution engine |
| `rich` | `[full]` | Colored tables, progress bars |
| `InquirerPy` | `[full]` | Interactive operation picker |
| `testcontainers` | `[full]` | Schema verification for optimizer |
| `psycopg` | `[full]` | PostgreSQL driver for batch tracking |

## Architecture

MigChain follows hexagonal architecture (ports & adapters):

```
presentation/         CLI parsing, Rich/Plain output
application/          Service orchestration, config
domain/               Pure logic: analyzer, planner, graph, optimizer, dependency resolver
infrastructure/       yoyo adapters, PostgreSQL batch tracker, testcontainers
```

All domain logic is framework-free. Infrastructure adapters implement domain ports (protocols)
and can be swapped without touching business logic.

## License

MIT
