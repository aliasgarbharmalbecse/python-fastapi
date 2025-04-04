from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers.departments import department_routes
from routers.users import role_routes, users_routes
from routers import auth_routes


# Define lifespan function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application Starting Up")
    yield
    print("Application is shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(auth_routes.router)
app.include_router(department_routes.router)
app.include_router(role_routes.router)
app.include_router(users_routes.router)
