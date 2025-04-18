from sqlalchemy.orm import Session
from typing import List, Type, Any
from models.user_model import User
from utilities.access_control_utils import is_god, check_hierarchy_access, check_department_access

def get_accessible_users(db: Session, current_user: User) -> list[Type[User]]:

    # If the user has the god role, return all users
    if is_god(current_user):
        return db.query(User).all()

    all_users = db.query(User).filter(User.is_active.is_(True)).all()
    accessible_users = []

    for user in all_users:
        if user.id == current_user.get('sub'):
            accessible_users.append(user)
            continue

        #hierarchy access won't work and also department need to work further

        if check_department_access(current_user, user) and check_hierarchy_access(current_user, user):
            accessible_users.append(user)

    return accessible_users
