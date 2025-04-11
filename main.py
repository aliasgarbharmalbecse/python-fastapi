from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session

from configurations.startup_task import sync_permissions_to_db
from routers.departments import department_routes
from routers.users import role_routes, users_routes, permissions_routes
from routers.attendance import attendance_routes
from routers import auth_routes
from configurations.database import SessionLocal


# Define lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Starting Up")
    db = SessionLocal()
    sync_permissions_to_db(db)
    db.close()
    yield
    print("Application is shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_routes.router)
app.include_router(department_routes.router)
app.include_router(role_routes.router)
app.include_router(permissions_routes.router)
app.include_router(users_routes.router)
app.include_router(attendance_routes.router)