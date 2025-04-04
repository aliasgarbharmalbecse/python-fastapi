import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session
from schemas.users_schema import RoleCreate, RoleUpdate
from models.user_model import Role


class RoleRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_role(self, role: RoleCreate):
        existing_role = self.db.query(Role).filter(Role.name == role.name).first()
        if existing_role:
            raise HTTPException(status_code=400, detail="Role already exists")
        new_role = Role(name=role.name.casefold())
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
            return role
        raise HTTPException(status_code=404, detail="role doesn't exist")

    def update_role(self, role: RoleUpdate):
        role_data = self.db.query(Role).filter(Role.id == role.id).first()
        if role_data is None:
            raise HTTPException(status_code=404, detail="role doesn't exist")
        role_data.name = role.name.casefold()
        self.db.commit()
        return True