from sqlalchemy.orm import Session
from models.user_model import Permission
from utilities.permission_utlis import all_registered_permissions


def sync_permissions_to_db(db: Session):
    existing_permissions = db.query(Permission.name).all()
    existing_permission_names = {perm[0] for perm in existing_permissions}

    new_permissions = [
        Permission(name=perm_name)
        for perm_name in all_registered_permissions
        if perm_name not in existing_permission_names
    ]

    if new_permissions:
        db.bulk_save_objects(new_permissions)
        db.commit()
