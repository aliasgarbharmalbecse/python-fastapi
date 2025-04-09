import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path
from sqlalchemy.orm import Session
from starlette import status
from schemas.users_schema import RolePermissionAssign
from repositories.users.roles_repository import RoleRepository
from configurations.database import get_db

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_permissions(db: Session = Depends(get_db)):
    role_repo = RoleRepository(db)
    return role_repo.get_all_permissions()

@router.post("/assign", status_code=status.HTTP_201_CREATED)
async def assign_permissions(permissions: RolePermissionAssign, db: Session = Depends(get_db)):
    role_repo = RoleRepository(db)
    return role_repo.assign_permissions(permissions)

