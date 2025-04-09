import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.users_schema import RoleCreate, RoleUpdate, RolePermissionAssign
from models.user_model import Role, Permission


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role: RoleCreate):
        existing_role = self.db.query(Role).filter(Role.name == role.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role already exists")
        new_role = Role(
            name=role.name.casefold(),
            hierarchy_level=role.hierarchy_level,
            can_cross_departments=role.can_cross_departments,
        )
        self.db.add(new_role)
        self.db.commit()
        self.db.refresh(new_role)
        return new_role

    def get_all_roles(self) -> list:
        return self.db.query(Role).all()

    def delete_role(self, name: str):
        role = self.db.query(Role).filter(Role.name == name.casefold()).first()
        if role:
            self.db.delete(role)
            self.db.commit()
            return role.name
        raise HTTPException(status_code=404, detail="role doesn't exist")

    def update_role(self, role: RoleUpdate):
        role_data = self.db.query(Role).filter(Role.id == role.id).first()
        if role_data is None:
            raise HTTPException(status_code=404, detail="role doesn't exist")
        role_data.name = role.name.casefold()
        role_data.hierarchy_level = role.hierarchy_level
        role_data.can_cross_departments = role.can_cross_departments
        self.db.commit()
        return True

    def assign_permissions(self, data: RolePermissionAssign):
        role = self.db.query(Role).filter(Role.id == data.role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        # Fetch all permissions by ID
        permissions = self.db.query(Permission).filter(Permission.id.in_(data.permission_ids)).all()
        if not permissions or len(permissions) != len(data.permission_ids):
            raise HTTPException(status_code=404, detail="One or more permissions not found")

        # Assign (override existing ones if needed)
        role.permissions = permissions
        self.db.commit()

        return {"message": f"Assigned {len(permissions)} permissions to role '{role.name}'"}

    def get_all_permissions(self):
        return self.db.query(Permission).all()