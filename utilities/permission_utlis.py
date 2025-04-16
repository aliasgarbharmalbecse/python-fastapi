# permissions.py
from fastapi import Depends, HTTPException, Request
from typing import Callable, Dict, Set

from sqlalchemy.orm import Session

from configurations.database import get_db
from models.user_model import User
from repositories.users.users_repository import UserRepository
from utilities.access_control_utils import has_required_permission, check_department_access, check_hierarchy_access, \
    is_god
from utilities.auth_utlis import verify_access_token

# Registry to track which endpoints use which permissions
permission_registry: Dict[str, str] = {}
all_registered_permissions: Set[str] = set()


# Register a permission with an endpoint
def register_permission(permission: str):
    def decorator(func: Callable):
        final_permission = permission or func.__name__
        permission_registry[func.__name__] = final_permission
        all_registered_permissions.add(final_permission)
        return func

    return decorator


# Query all permissions for the user from their roles
def get_user_permissions(user: User) -> Set[str]:
    permissions = set()
    for resource in user.get("permissions"):
        permissions.add(resource)
    return permissions


# Main permission enforcement dependency
def enforce_permissions_dependency(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(verify_access_token),
):

    #user with role 0 has access to everything
    if is_god(current_user):
        return current_user

    endpoint_func = request.scope.get("endpoint")
    func_name = endpoint_func.__name__ if endpoint_func else None

    if func_name:
        endpoint_permission = permission_registry.get(func_name)
        if endpoint_permission and not has_required_permission(current_user, endpoint_permission):
            raise HTTPException(status_code=403, detail="Permission denied")

    # Check if the route targets a specific user
    target_user_id = request.path_params.get("user_id")

    if target_user_id:
        user_repo = UserRepository(db)
        target_user = user_repo.get_user_by_id(target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Department-level access
        if not check_department_access(current_user, target_user):
            raise HTTPException(status_code=403, detail="Cross-department access denied")

        # Hierarchy-level access
        if not check_hierarchy_access(current_user, target_user):
            raise HTTPException(status_code=403, detail="Insufficient role hierarchy")

    return current_user
