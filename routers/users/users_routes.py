from fastapi import APIRouter, Depends, Path
from pydantic import UUID4
from starlette import status

from schemas.users_schema import UserCreate, UserResponse, UserUpdate
from sqlalchemy.orm import Session
from configurations.database import get_db
from repositories.users.users_repository import UserRepository
from utilities.permission_utlis import register_permission, enforce_permissions_dependency
from models.user_model import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post('/create', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@register_permission('create_user')
async def create_user(
        user_data: UserCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    user_repo = UserRepository(db)
    return user_repo.create_user(user_data)

@router.get('/', status_code=status.HTTP_200_OK)
@register_permission('get_all_users')
async def get_all_users(db: Session = Depends(get_db), current_user: User = Depends(enforce_permissions_dependency)):
    user = UserRepository(db)
    return user.get_all_users()

@router.get('/{user_id}', response_model=UserResponse, status_code=status.HTTP_200_OK)
@register_permission('get_user_by_id')
async def get_user_by_id(
        user_id: UUID4 = Path(),
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    return UserResponse(
        id=user.id,
        firstname=user.firstname,
        lastname=user.lastname,
        email=user.email,
        phone=user.phone,
        roles=[{
            "name": user_role.role.name,
            "id": user_role.role.id,
            "hierarchy_level": user_role.role.hierarchy_level,
            "can_cross_departments": user_role.role.can_cross_departments
        } for user_role in user.roles],
        # Extract role names correctly
        department_name=user.department.department_name if user.department else None,
        department={"id": user.department.id, "name": user.department.department_name} if user.department else None,
        timezone=user.timezone if user.timezone else None
    )

@router.put('/update', status_code=status.HTTP_201_CREATED)
@register_permission('update_user')
async def update_user(
        user_data: UserUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(enforce_permissions_dependency)
):
    ## This api needs to change. Currently this doesn't work correctly.
    user = UserRepository(db)
    return user.update_user(user_data)


## to be done
## inactivate user, assign role, change password