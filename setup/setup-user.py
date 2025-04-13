import sys
import os
from sqlalchemy.orm import Session
import uuid
from passlib.context import CryptContext

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configurations.database import SessionLocal, engine, Base
from models.user_model import User, Role, UserRole, Department

# Initialize password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Setup Values ---
DEFAULT_DEPARTMENT_NAME = "General"
DEFAULT_ROLE_NAME = "Admin"
DEFAULT_USER_EMAIL = "admin@example.com"
DEFAULT_USER_PASSWORD = "SuperAdmin@123!"
DEFAULT_USER_FIRSTNAME = "Admin"
DEFAULT_USER_LASTNAME = "User"
DEFAULT_PHONE = "1212121212"

def create_initial_setup(db: Session):
    # 1. Create Department
    department = db.query(Department).filter_by(department_name=DEFAULT_DEPARTMENT_NAME).first()
    if not department:
        department = Department(department_name=DEFAULT_DEPARTMENT_NAME)
        db.add(department)
        db.commit()
        db.refresh(department)

    # 2. Create Role
    role = db.query(Role).filter_by(name=DEFAULT_ROLE_NAME).first()
    if not role:
        role = Role(name=DEFAULT_ROLE_NAME, hierarchy_level=0, can_cross_departments=True)
        db.add(role)
        db.commit()
        db.refresh(role)

    # 3. Create User
    user = db.query(User).filter_by(email=DEFAULT_USER_EMAIL).first()
    if not user:
        hashed_pw = pwd_context.hash(DEFAULT_USER_PASSWORD)
        user = User(
            firstname=DEFAULT_USER_FIRSTNAME,
            lastname=DEFAULT_USER_LASTNAME,
            email=DEFAULT_USER_EMAIL,
            hashed_password=hashed_pw,
            department_id=department.id,
            phone=DEFAULT_PHONE
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # 4. Assign Role to User
        user_role = UserRole(user_id=user.id, role_id=role.id)
        db.add(user_role)
        db.commit()

        print(f"✅ User '{DEFAULT_USER_EMAIL}' created and assigned to role '{DEFAULT_ROLE_NAME}' and department '{DEFAULT_DEPARTMENT_NAME}'")
    else:
        print(f"ℹ️ User '{DEFAULT_USER_EMAIL}' already exists.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        create_initial_setup(db)
    finally:
        db.close()
