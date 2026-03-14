from fastapi import APIRouter
from app.api.v1.endpoints import auth
from app.api.v1.endpoints import users

router = APIRouter()
router.include_router(auth.router, tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
