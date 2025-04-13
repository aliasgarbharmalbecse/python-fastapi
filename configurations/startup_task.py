from sqlalchemy.orm import Session
from models.user_model import Permission
from utilities.permission_utlis import all_registered_permissions


def sync_permissions_to_db(db: Session, delete_orphans: bool = False):
    existing_permissions = db.query(Permission.name).all()
    existing_permission_names = {name for (name,) in existing_permissions}

    new_permissions = [
        Permission(name=perm_name)
        for perm_name in all_registered_permissions
        if perm_name not in existing_permission_names
    ]

    try:
        if new_permissions:
            db.bulk_save_objects(new_permissions)
            db.commit()
            print(f"Inserted {len(new_permissions)} new permissions")

        if delete_orphans:
            orphaned_permissions = existing_permission_names - set(all_registered_permissions)
            if orphaned_permissions:
                db.query(Permission).filter(Permission.name.in_(orphaned_permissions)).delete(synchronize_session=False)
                db.commit()
                print(f"Deleted {len(orphaned_permissions)} orphaned permissions")

    except Exception as e:
        db.rollback()
        print(f"Error syncing permissions: {e}")
