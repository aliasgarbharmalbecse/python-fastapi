import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path
from sqlalchemy.orm import Session
from starlette import status

from models.user_model import User
from schemas.users_schema import RoleCreate, RoleUpdate
from repositories.users.roles_repository import RoleRepository
from configurations.database import get_db
from utilities.permission_utlis import register_permission, enforce_permissions_dependency

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)


#create department
@router.post("/create", status_code=status.HTTP_201_CREATED)
@register_permission('create_role')
async def create_role(
        role: RoleCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    role_repo = RoleRepository(db)
    return role_repo.create_role(role)


#get department
@router.get("/", status_code=status.HTTP_200_OK)
@register_permission('get_all_roles')
async def get_all_roles(db: Session = Depends(get_db), current_user: User = Depends(enforce_permissions_dependency)):
    role_repo = RoleRepository(db)
    return role_repo.get_all_roles()
    pass


#update department
@router.put("/update/", status_code=status.HTTP_201_CREATED)
@register_permission('update_role')
async def update_role(
        role: RoleUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    role_repo = RoleRepository(db)
    return role_repo.update_role(role)
    pass


# Delete role by name
@router.delete("/deleteByName/{role_name}", status_code=status.HTTP_200_OK)
@register_permission('delete_role')
async def delete_role(
        role_name: str = Path(..., description="Name of Role (case insensitive)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    role_repo = RoleRepository(db)
    return role_repo.delete_role(role_name)
