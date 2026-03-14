"""
DynamoDB Migration Runner
=========================
Usage:
    python migrate.py            → run all pending migrations (migrate up)
    python migrate.py --status   → show applied vs pending migrations
    python migrate.py --rollback 0001_create_users_table  → roll back a specific migration

How it works:
  1. Ensures a `schema_migrations` table exists in DynamoDB.
  2. Scans that table to see which migrations have already been applied.
  3. Discovers all migration files in the `migrations/` folder (sorted by name).
  4. Runs only the pending ones, in order.
  5. Records each successful migration with a timestamp.

Migration file format (see migrations/0001_*.py for example):
  - MIGRATION_ID: str     — unique identifier (same as filename without .py)
  - DESCRIPTION:  str     — human-readable description
  - def up(client, table_name: str)   — apply the migration
  - def down(client, table_name: str) — rollback the migration
"""

import importlib
import importlib.util
import sys
import os
from datetime import datetime, timezone
from pathlib import Path

# Make sure app/ is importable when running migrate.py from the project root
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.db.database import get_dynamodb_client

MIGRATIONS_TABLE = "schema_migrations"
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


# ─── Schema Migrations Table ──────────────────────────────────────────────────

def ensure_migrations_table(client):
    """Create the schema_migrations tracker table if it doesn't exist."""
    existing = client.list_tables()["TableNames"]
    if MIGRATIONS_TABLE in existing:
        return
    print(f"  Creating migration tracker table '{MIGRATIONS_TABLE}'...")
    client.create_table(
        TableName=MIGRATIONS_TABLE,
        KeySchema=[
            {"AttributeName": "migration_id", "KeyType": "HASH"},
        ],
        AttributeDefinitions=[
            {"AttributeName": "migration_id", "AttributeType": "S"},
        ],
        BillingMode="PAY_PER_REQUEST",
    )
    waiter = client.get_waiter("table_exists")
    waiter.wait(TableName=MIGRATIONS_TABLE)
    print(f"  ✅ Tracker table '{MIGRATIONS_TABLE}' ready.")


def get_applied_migrations(client) -> dict:
    """
    Return a dict of { migration_id: { applied_at, description } }
    for all migrations already recorded in schema_migrations.
    """
    from boto3 import resource as boto3_resource
    dynamo = boto3_resource(
        "dynamodb",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    table = dynamo.Table(MIGRATIONS_TABLE)
    response = table.scan()
    applied = {}
    for item in response.get("Items", []):
        applied[item["migration_id"]] = item
    return applied


def record_migration(client, migration_id: str, description: str):
    """Mark a migration as applied in the schema_migrations table."""
    from boto3 import resource as boto3_resource
    dynamo = boto3_resource(
        "dynamodb",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    table = dynamo.Table(MIGRATIONS_TABLE)
    table.put_item(Item={
        "migration_id": migration_id,
        "description": description,
        "applied_at": datetime.now(timezone.utc).isoformat(),
    })


def remove_migration_record(client, migration_id: str):
    """Remove a migration record (used during rollback)."""
    from boto3 import resource as boto3_resource
    dynamo = boto3_resource(
        "dynamodb",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    table = dynamo.Table(MIGRATIONS_TABLE)
    table.delete_item(Key={"migration_id": migration_id})


# ─── Migration Discovery ───────────────────────────────────────────────────────

def discover_migrations() -> list[Path]:
    """Return all migration files sorted by filename (order matters)."""
    return sorted(MIGRATIONS_DIR.glob("[0-9]*.py"))


def load_migration(path: Path):
    """Dynamically import a migration module from its file path."""
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load migration from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


# ─── Commands ─────────────────────────────────────────────────────────────────

def cmd_status(client):
    """Show which migrations are applied and which are pending."""
    ensure_migrations_table(client)
    applied = get_applied_migrations(client)
    migrations = discover_migrations()

    print("\n📋  Migration Status")
    print("─" * 60)
    if not migrations:
        print("  No migration files found in migrations/")
        return

    for path in migrations:
        mod = load_migration(path)
        mid = mod.MIGRATION_ID
        desc = mod.DESCRIPTION
        if mid in applied:
            when = applied[mid].get("applied_at", "unknown time")
            print(f"  ✅  [APPLIED]  {mid}")
            print(f"                {desc}")
            print(f"                applied at: {when}")
        else:
            print(f"  ⏳  [PENDING]  {mid}")
            print(f"                {desc}")
        print()
    print("─" * 60)


def cmd_migrate(client):
    """Run all pending migrations in order."""
    ensure_migrations_table(client)
    applied = get_applied_migrations(client)
    migrations = discover_migrations()

    pending = [m for m in migrations if load_migration(m).MIGRATION_ID not in applied]

    if not pending:
        print("  ✅  All migrations are up to date. Nothing to run.")
        return

    print(f"\n🚀  Running {len(pending)} pending migration(s)...\n")
    for path in pending:
        mod = load_migration(path)
        mid = mod.MIGRATION_ID
        desc = mod.DESCRIPTION
        print(f"  ⚙   Applying: {mid}")
        print(f"      {desc}")
        try:
            mod.up(client, settings.DYNAMODB_TABLE)
            record_migration(client, mid, desc)
            print(f"  ✅  Done: {mid}\n")
        except Exception as e:
            print(f"  ❌  FAILED: {mid} — {e}")
            print("      Stopping. Fix the error and re-run.\n")
            sys.exit(1)

    print("✅  All migrations applied successfully.")


def cmd_rollback(client, target_migration_id: str):
    """Roll back a specific migration by ID."""
    ensure_migrations_table(client)
    applied = get_applied_migrations(client)

    if target_migration_id not in applied:
        print(f"  ⚠️   Migration '{target_migration_id}' is not in the applied list.")
        return

    # Find the migration file
    migrations = {load_migration(p).MIGRATION_ID: p for p in discover_migrations()}
    if target_migration_id not in migrations:
        print(f"  ❌  Migration file for '{target_migration_id}' not found.")
        return

    mod = load_migration(migrations[target_migration_id])
    print(f"\n⏪  Rolling back: {target_migration_id}")
    print(f"    {mod.DESCRIPTION}\n")
    try:
        mod.down(client, settings.DYNAMODB_TABLE)
        remove_migration_record(client, target_migration_id)
        print(f"  ✅  Rolled back: {target_migration_id}")
    except Exception as e:
        print(f"  ❌  Rollback FAILED: {e}")
        sys.exit(1)


# ─── Entry Point ──────────────────────────────────────────────────────────────

def run_migrations_on_startup():
    """
    Called automatically from the FastAPI lifespan.
    Only runs pending migrations — safe to call every time the server starts.
    """
    client = get_dynamodb_client()
    ensure_migrations_table(client)
    applied = get_applied_migrations(client)
    migrations = discover_migrations()
    pending = [m for m in migrations if load_migration(m).MIGRATION_ID not in applied]

    if not pending:
        print("  ✅  DB is up to date — no pending migrations.")
        return

    print(f"  ⚙   Found {len(pending)} pending migration(s) — applying now...")
    for path in pending:
        mod = load_migration(path)
        mid = mod.MIGRATION_ID
        try:
            mod.up(client, settings.DYNAMODB_TABLE)
            record_migration(client, mid, mod.DESCRIPTION)
            print(f"  ✅  Applied: {mid}")
        except Exception as e:
            print(f"  ❌  Failed to apply migration '{mid}': {e}")
            raise


if __name__ == "__main__":
    client = get_dynamodb_client()

    if "--status" in sys.argv:
        cmd_status(client)
    elif "--rollback" in sys.argv:
        idx = sys.argv.index("--rollback")
        if idx + 1 >= len(sys.argv):
            print("Usage: python migrate.py --rollback <migration_id>")
            sys.exit(1)
        target = sys.argv[idx + 1]
        cmd_rollback(client, target)
    else:
        cmd_migrate(client)
