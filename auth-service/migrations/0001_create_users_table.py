"""
Migration: 0001_create_users_table
Description: Initial migration — creates the `users` table with email as partition key.

Schema:
  - PK: email (String)          — user's email, unique identifier
  - Attributes (schemaless, added at runtime):
      id           (String)  — UUID
      hashed_password (String)
      is_active    (Boolean) — default True
      is_superuser (Boolean) — default False

Indexes:
  - No GSI for now (can be added in future migrations)
"""

MIGRATION_ID = "0001_create_users_table"
DESCRIPTION = "Initial migration — creates the users table"


def up(client, table_name: str):
    """Create the users table (idempotent — skips if already exists)."""
    try:
        client.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "email", "KeyType": "HASH"},
            ],
            AttributeDefinitions=[
                {"AttributeName": "email", "AttributeType": "S"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = client.get_waiter("table_exists")
        waiter.wait(TableName=table_name)
        print(f"    Table '{table_name}' created.")
    except client.exceptions.ResourceInUseException:
        print(f"    Table '{table_name}' already exists — recorded as applied.")


def down(client, table_name: str):
    """Drop the users table (rollback)."""
    client.delete_table(TableName=table_name)
    waiter = client.get_waiter("table_not_exists")
    waiter.wait(TableName=table_name)
    print(f"    Table '{table_name}' deleted.")
