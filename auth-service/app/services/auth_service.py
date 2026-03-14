from typing import Optional, Any
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password
import uuid

def get_user_by_email(table: Any, email: str) -> Optional[User]:
    response = table.get_item(Key={'email': email})
    item = response.get('Item')
    if item:
        return User(**item)
    return None

def create_user(table: Any, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    user_id = str(uuid.uuid4())
    db_user = User(
        id=user_id,
        email=user.email,
        hashed_password=hashed_password,
        is_active=user.is_active,
        is_superuser=user.is_superuser
    )
    # Using model_dump() for Pydantic v2
    table.put_item(Item=db_user.model_dump())
    return db_user

def authenticate_user(table: Any, email: str, password: str) -> Optional[User]:
    user = get_user_by_email(table, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
