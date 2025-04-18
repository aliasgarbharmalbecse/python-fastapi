from fastapi import HTTPException
from models.user_model import User
from repositories.users.users_repository import UserRepository
from schemas.users_schema import UserResponse


def has_required_permission(user, endpoint_permission: str) -> bool:
    return endpoint_permission in user.get("permissions", [])


#this can have problem with lower role have access to higher role cross department
def can_access_cross_department(user: dict) -> bool:
    return any(ctx.get("can_cross_departments", False) for ctx in user.get("access_context", []))


def get_user_min_hierarchy_from_token(user_dict: dict) -> int:
    access_context = user_dict.get("access_context", [])

    if not access_context:
        raise HTTPException(status_code=403, detail="User has no access roles")

    return min(ctx.get("hierarchy_level", 999) for ctx in access_context)


def get_user_min_hierarchy_from_db(user_model) -> int:
    return (
        min((user_role.role.hierarchy_level for user_role in user_model.roles), default=999)
    )

def check_department_access(current_user, target_user) -> bool:
    department = target_user.department
    if not department or not department.id:
        return False
    return (
            current_user.get("department") == department.department_name
            or can_access_cross_department(current_user)
    )


def check_hierarchy_access(current_user, target_user: User) -> bool:
    current_level = get_user_min_hierarchy_from_token(current_user)
    target_level = get_user_min_hierarchy_from_db(target_user)
    return current_level <= target_level


def is_god(current_user) -> bool:
    return any(ctx.get("hierarchy_level", 999) == 0 for ctx in current_user.get("access_context", []))
