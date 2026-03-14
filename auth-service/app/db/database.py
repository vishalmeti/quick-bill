import boto3
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource

from app.core.config import settings


def get_dynamodb_resource() -> DynamoDBServiceResource:
    return boto3.resource(
        "dynamodb",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )


def get_dynamodb_client():
    return boto3.client(
        "dynamodb",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )

def get_users_table():
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.DYNAMODB_TABLE)

def get_db():
    # In DynamoDB we don't need a persistent session like SQLAlchemy.
    # We yield the table directly to make it easy for endpoints.
    table = get_users_table()
    yield table

def create_tables():
    client = get_dynamodb_client()
    try:
        existing_tables = client.list_tables()['TableNames']
        if settings.DYNAMODB_TABLE in existing_tables:
            print(f"  ✔  Table '{settings.DYNAMODB_TABLE}' already exists — skipping creation.")
            return

        print(f"  ⚙  Table '{settings.DYNAMODB_TABLE}' not found — creating...")
        client.create_table(
            TableName=settings.DYNAMODB_TABLE,
            KeySchema=[
                {
                    'AttributeName': 'email',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'email',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing, no capacity planning needed
        )
        waiter = client.get_waiter('table_exists')
        waiter.wait(TableName=settings.DYNAMODB_TABLE)
        print(f"  ✅  Table '{settings.DYNAMODB_TABLE}' created successfully.")
    except Exception as e:
        print(f"  ❌  Error with DynamoDB table setup: {e}")
        raise

