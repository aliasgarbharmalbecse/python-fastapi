from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from configurations.startup_task import sync_permissions_to_db
from routers.departments import department_routes
from routers.users import role_routes, users_routes, permissions_routes
from routers.attendance import attendance_routes
from routers import auth_routes
from routers.leaves import leaves_route
from configurations.database import SessionLocal
from utilities import redis_cache
import os
from dotenv import load_dotenv

load_dotenv()

# Define lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Starting Up")
    db = SessionLocal()
    sync_permissions_to_db(db)
    db.close()

    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_port = int(os.getenv("REDIS_PORT", "6379"))
    redis_password = os.getenv("REDIS_PASSWORD", None)
    redis_db = int(os.getenv("REDIS_DB", "0"))

    await redis_cache.setup_redis(
        host=redis_host,
        port=redis_port,
        password=redis_password,
        db=redis_db
    )

    yield
    print("Application is shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_routes.router)
app.include_router(department_routes.router)
app.include_router(role_routes.router)
app.include_router(permissions_routes.router)
app.include_router(users_routes.router)
app.include_router(attendance_routes.router)
app.include_router(leaves_route.router)