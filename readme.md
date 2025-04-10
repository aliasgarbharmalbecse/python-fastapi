User Module

database tables to be created
- users
  - id: uuid
  - firstname
  - lastname
  - email
  - phone
  - department [fk to department id]
  - role
  - is_active
  - hashed_password
  - created_at
- departments
  - id: uuid
  - department_name
  - department_head: ref users:id
  - users: relationship with users
- roles
  - admin
  - manager
  - employee
- user_roles
  - id
  - user_id
  - role_id

RBAC implementation step

- Each role is linked to one or more permissions.
- Users are assigned one or more roles.
- Each endpoint can register a required permission using a custom decorator.
- When a request is made, the system:
Authenticates the user using a JWT token.
Loads the user’s roles and permissions.
Checks if the user has the necessary permission.
Optionally validates resource-level access (e.g., managers only accessing users in their department).

🧠 Decorator-Based Permission Mapping
To define which permission is required for an endpoint, use the `@register_permission()` decorator.
```
@router.get('/protected-route')
@register_permission("view_user")
def test_method(current_user: User = Depends(enforce_permissions_dependency)):
    return {"message": "You have access!"}
```

This will:

- Automatically register the endpoint name (test_method) to the permission view_user.
- The enforce_permissions_dependency will check this permission at request time.
- If the user does not have this permission, a 403 Forbidden response is returned.

🛠 How to Add a New Permission for an Endpoint
1. Create the permission in the database (if not already present):

```INSERT INTO permissions (name) VALUES ('create_user');```

2. Assign this permission to a role:

``` INSERT INTO permissions (name) VALUES ('create_user');```
 
3. Decorate your endpoint:
```python
@router.post('/create')
@register_permission("create_user")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(enforce_permissions_dependency)
):
    return user_repo.create_user(user_data)
```

🔐 Optional: Resource-Level Access Control

You can also include logic to restrict access based on department, manager, etc.

```python
if not can_create_user(current_user, user_data):
    raise HTTPException(status_code=403, detail="Not allowed to create user in this department")
```

🔁 How to View Registered Endpoint Permissions
The permission_registry dictionary contains the mapping:

```python
from utilities.permissions import permission_registry

print(permission_registry)
# Output: {'create_user': 'create_user', 'test_method': 'check_user', ...}
```

``User with all permissions``
A user role with hierarchy level as 0 will be able to access everything. 
```Neve give any role hirerachy 0 unless you want them to access everything.```