import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path
from sqlalchemy.orm import Session
from starlette import status
from schemas.users_schema import RoleCreate, RoleUpdate
from repositories.users.roles_repository import RoleRepository
from configurations.database import get_db

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

#create department
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_role(role: RoleCreate, db: Session = Depends(get_db)):
    role_repo = RoleRepository(db)
    return role_repo.create_role(role)


#get department
@router.get("/", status_code=status.HTTP_200_OK)
async def get_all_roles(db: Session = Depends(get_db)):
    role_repo = RoleRepository(db)
    return role_repo.get_all_roles()
    pass


#update department
@router.put("/update/", status_code=status.HTTP_201_CREATED)
async def update_role(role: RoleUpdate, db: Session = Depends(get_db)):
    role_repo = RoleRepository(db)
    return role_repo.update_role(role)
    pass

# Delete department by name
@router.delete("/deleteByName/{department_name}", status_code=status.HTTP_200_OK)
async def delete_role(
    department_name: str = Path(..., description="Name of Role (case insensitive)"),
    db: Session = Depends(get_db),
):
    role_repo = RoleRepository(db)
    return role_repo.delete_role(department_name)
