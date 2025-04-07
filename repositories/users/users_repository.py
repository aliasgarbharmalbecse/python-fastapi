import uuid

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from schemas.users_schema import UserCreate, UserResponse, UserUpdate, UserValidateResponse
from models.user_model import User, UserRole, Role, Department
from utilities.auth_utlis import get_password_hash


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate):
        ##check if user exists. User lower() because casefold() also does special chars conversion which we don't want
        user_exists = self.db.query(User).filter(User.email == user_data.email.lower()).first()
        if user_exists:
            raise HTTPException(status_code=400, detail="User already exists")

        if user_data.phone:
            phone_exists = self.db.query(User).filter(User.phone == user_data.phone).first()
            if phone_exists:
                raise HTTPException(status_code=400, detail="User with this phone number already exists")

        ## create password hash
        password_hash = get_password_hash(user_data.password)

        ##get roles and check if they exists. Create new if they don't and retunr them in array
        roles = []
        for role_id in user_data.roles:
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                raise HTTPException(status_code=400, detail=f"Role with id {role_id} doesn't exist")

            roles.append(role)

        # Create or fetch department
        department = None
        if user_data.department_name:
            department = self.db.query(Department).filter(
                Department.department_name == user_data.department_name).first()
            if not department:
                department = Department(department_name=user_data.department_name)
                self.db.add(department)
                self.db.flush()  # Ensure department has an ID

        ## create user along with roles.
        user = User(
            firstname=user_data.firstname,
            lastname=user_data.lastname,
            email=user_data.email,
            phone=user_data.phone,
            hashed_password=password_hash,
            department_id=department.id if department else None,
            reports_to=user_data.reports_to if user_data.reports_to else None,
            roles=[UserRole(role_id=role.id) for role in roles]
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserResponse(
            id=user.id,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            phone=user.phone,
            roles=[{"name": role.name, "id": role.id} for role in roles],
            reports_to=user.reports_to,
            department_name=department.department_name if department else None
        )

    def get_all_users(self):
        users = (self.db.query(User)
                 .options(selectinload(User.roles).selectinload(UserRole.role))
                 .options(selectinload(User.department))
                 .all())
        return users

    def get_user_by_email(self, email_id):
        user = (
            self.db.query(User)
            .options(selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.permissions))
            .options(selectinload(User.department))  # Load department
            .filter(User.email == email_id)
            .first()
        )

        if user is None:
            raise HTTPException(status_code=404, detail="User doesn't exist")

        # Extract permissions from roles
        permissions_set = set()
        for user_role in user.roles:
            for permission in user_role.role.permissions:
                permissions_set.add(permission.name)

        return UserValidateResponse(
            id=user.id,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            phone=user.phone,
            hashed_password=user.hashed_password,
            roles=[{"name": user_role.role.name, "id": user_role.role.id} for user_role in user.roles],
            # Extract role names correctly
            department_name=user.department.department_name if user.department else None,
            permissions=list(permissions_set)
        )

    def get_user_by_id(self, id):
        user = (
            self.db.query(User)
            .options(selectinload(User.roles).selectinload(UserRole.role).selectinload(Role.permissions))
            .options(selectinload(User.department))  # Load department
            .filter(User.id == id)
            .first()
        )

        if user is None:
            raise HTTPException(status_code=404, detail="User doesn't exist")

        # Extract permissions from roles
        permissions_set = set()
        for user_role in user.roles:
            for permission in user_role.role.permissions:
                permissions_set.add(permission.name)

        return UserResponse(
            id=user.id,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            phone=user.phone,
            roles=[{"name": user_role.role.name, "id": user_role.role.id} for user_role in user.roles],
            # Extract role names correctly
            department_name=user.department.department_name if user.department else None,
            permissions=list(permissions_set)
        )

    def update_user(self, user_data: UserUpdate):
        # Fetch existing user
        user = (
            self.db.query(User)
            .options(selectinload(User.roles))
            .options(selectinload(User.department))
            .filter(User.email == user_data.email)
            .first()
        )

        if user is None:
            raise HTTPException(status_code=404, detail="User doesn't exist")

        # Update basic fields
        user.firstname = user_data.firstname or user.firstname
        user.lastname = user_data.lastname or user.lastname
        user.phone = user_data.phone or user.phone
        user.is_active = user_data.is_active if user_data.is_active is not None else user.is_active

        #update password if requested
        if user_data.password is not None:
            password_hash = get_password_hash(user_data.password)
            user.hashed_password = password_hash

        #update department by getting the id first
        department_new = self.db.query(Department).filter(
            Department.department_name == user_data.department_name).first()
        if department_new is not None:
            user.department_id = department_new.id

        # Commit first to ensure user_id is assigned before updating roles
        self.db.commit()
        self.db.refresh(user)  # Refresh user instance after commit

        ##get roles and check if they exists. Create new if they don't and retunr them in array
        roles = []
        for role_name in user_data.roles:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if role is not None:
                roles.append(role)

        # Remove all existing roles
        self.db.query(UserRole).filter(UserRole.user_id == user.id).delete()
        self.db.commit()  # Commit to reflect the deletion in the database

        # Assign new roles
        user.roles = [UserRole(user_id=user.id, role_id=role.id) for role in roles]

        # Commit again to save new roles
        self.db.commit()
        self.db.refresh(user)

        return UserResponse(
            id=user.id,
            firstname=user.firstname,
            lastname=user.lastname,
            email=user.email,
            phone=user.phone
        )