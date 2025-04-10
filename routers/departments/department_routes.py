from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Path
from sqlalchemy.orm import Session
from starlette import status

from models.user_model import User
from schemas.department_schema import DepartmentCreate, DepartmentUpdate, DepartmentResponse
from repositories.departments.department_repository import DepartmentRepository
from configurations.database import get_db
from utilities.permission_utlis import register_permission, enforce_permissions_dependency

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


#create department
@router.post("/create", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
@register_permission("create_department")
async def create_department(
        department: DepartmentCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    try:
        dept_repo = DepartmentRepository(db)
        return dept_repo.create_department(department)
    except Exception as e:
        print(f"{e}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


#get department
@router.get("/", status_code=status.HTTP_200_OK)
@register_permission("get_all_departments")
async def get_all_departments(
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    try:
        dept_repo = DepartmentRepository(db)
        return dept_repo.get_all_departments()
    except Exception as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST)


#update department
@router.put("/update/", status_code=status.HTTP_201_CREATED)
@register_permission("update_department")
async def update_department(
        department: DepartmentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    dept_repo = DepartmentRepository(db)
    result = dept_repo.update_department(department)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return {"message": "Department updated successfully"}


# Delete department by name
@router.delete("/deleteByName/{department_name}", status_code=status.HTTP_200_OK)
@register_permission('delete_department')
async def delete_department(
        department_name: str = Path(..., description="Name of department (case insensitive)"),
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    dept_repo = DepartmentRepository(db)
    result = dept_repo.delete_department(department_name)

    if not result:  # If department not found
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")

    return {"message": "Department deleted successfully"}
