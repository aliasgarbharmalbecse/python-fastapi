# permissions.py
from fastapi import Depends, HTTPException, Request
from typing import Callable, Dict, Set
from models.user_model import User
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
        user: User = Depends(verify_access_token),
):
    #Get the actual route handler function
    endpoint_func = request.scope.get("endpoint")
    func_name = endpoint_func.__name__ if endpoint_func else None
    if func_name:
        endpoint_permission = permission_registry.get(func_name)
        if endpoint_permission:
            user_permissions = get_user_permissions(user)
            if endpoint_permission not in user_permissions:
                raise HTTPException(status_code=403, detail="Permission denied")

    return user
