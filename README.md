# MigChain

Database migration management CLI tool built on top of [yoyo-migrations](https://ollycope.com/software/yoyo/latest/).

Features:
- Dependency graph analysis with cycle detection
- Phased execution (schema + inserter migrations)
- Batch tracking for `--rollback-latest`
- Domain-based filtering (`--include`, `--exclude`)
- Dry-run mode with JSON plan export
- Mermaid dependency graph visualization

## Installation

```bash
uv add migchain
# or
pip install migchain
```

## Usage

```bash
# Apply pending migrations
migchain --dsn postgresql://user:pass@localhost/mydb --apply

# Use DATABASE_URL env var
export DATABASE_URL=postgresql://user:pass@localhost/mydb
migchain --apply

# Rollback latest batch
migchain --rollback-latest

# Dry run with verbose output
migchain --dry-run -vv

# Filter by domain
migchain --include auth,billing --apply

# Export dependency graph
migchain --show-graph --graph-out deps.mmd

# Custom migrations directory
migchain --migrations-dir ./db/migrations --apply
```

## Configuration

| Flag | Env Var | Description |
|------|---------|-------------|
| `--dsn` | `DATABASE_URL` | PostgreSQL connection string |
| `--migrations-dir` | — | Path to migrations root (default: `./migrations`) |
| `--apply` | — | Apply pending migrations (default) |
| `--rollback` | — | Rollback all applied migrations |
| `--rollback-one` | — | Rollback one safe leaf migration |
| `--rollback-latest` | — | Rollback latest applied batch |
| `--reload` | — | Full reload: rollback all, then apply all |
| `--dry-run` | — | Show plan without executing |
| `--no-inserters` | — | Skip inserter migrations |
| `--include` | — | Comma-separated domains to include |
| `--exclude` | — | Comma-separated domains to exclude |
| `-v` / `-vv` | — | Increase verbosity |
| `--show-graph` | — | Print Mermaid dependency graph |
| `--graph-out` | — | Write graph to file |
| `--json-plan-out` | — | Export execution plan as JSON |

## License

MIT
