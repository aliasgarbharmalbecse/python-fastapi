import uuid

from sqlalchemy.orm import Session
from schemas.department_schema import DepartmentRequest, DepartmentUpdateRequest
from models.user_model import Department


class DepartmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_department(self, department_data: DepartmentRequest):
        new_department = Department(
            department_name=department_data.department_name.casefold(), #department is stored in lower case only
            department_head=department_data.department_head
        )
        self.db.add(new_department)
        self.db.commit()
        self.db.refresh(new_department)
        return new_department

    def get_all_departments(self) -> list:
        return self.db.query(Department).all()

    def delete_department(self, name: str) -> bool:
        department = self.db.query(Department).filter(Department.department_name == name.casefold()).first()
        if department is None:
            return False

        self.db.delete(department)
        self.db.commit()
        return True

    def update_department(self, department_data: DepartmentUpdateRequest):
        department = self.db.query(Department).filter(
            Department.id == department_data.id
        ).first()
        if department is None:
            return False
        department.department_name = department_data.department_name
        department.department_head = department_data.department_head
        self.db.commit()
        return True