from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import router as api_router
from app.db.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan handler — runs once at startup before the server accepts requests.
    DynamoDB equivalent of 'manage.py migrate': checks if tables exist and
    creates them if they don't. No separate migration step needed.
    """
    print("🚀 Starting up... checking / creating DynamoDB tables.")
    create_tables()
    print("✅ DynamoDB tables ready.")
    yield
    # (Optional) teardown logic can go here after the yield
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
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
