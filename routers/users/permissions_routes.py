import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path
from sqlalchemy.orm import Session
from starlette import status

from models.user_model import User
from schemas.users_schema import RolePermissionAssign
from repositories.users.roles_repository import RoleRepository
from configurations.database import get_db
from utilities.permission_utlis import enforce_permissions_dependency, register_permission

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"]
)


@router.get("/", status_code=status.HTTP_200_OK)
@register_permission('get_all_permissions')
async def get_all_permissions(
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    role_repo = RoleRepository(db)
    return role_repo.get_all_permissions()

@router.post("/assign", status_code=status.HTTP_201_CREATED)
@register_permission('assign_permissions')
async def assign_permissions(
        permissions: RolePermissionAssign,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    role_repo = RoleRepository(db)
    return role_repo.assign_permissions(permissions)


## get role permissions endpoint to be implemented to check which role has which permissions