import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import router as api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan handler — runs once at startup before the server accepts requests."""
    print("🚀 Starting up.")
    yield
    print("🛑 Shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Authentication Microservice for Quick Bill",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Quick Bill Auth Service"}


if __name__ == "__main__":
    if "--migrate-status" in sys.argv:
        from app.db.database import get_dynamodb_client
        from migrate import cmd_status

        client = get_dynamodb_client()
        cmd_status(client)
        sys.exit(0)

    if "--migrate" in sys.argv:
        from app.db.database import get_dynamodb_client
        from migrate import cmd_migrate
        print("🚀 Running migrations...")
        client = get_dynamodb_client()
        cmd_migrate(client)
        print("✅ Migrations completed.")
        sys.exit(0)

    print("🚀 Starting server...")
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    print("✅ Server started.")
