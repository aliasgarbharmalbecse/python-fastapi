from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from starlette import status
from schemas.auth_schema import AuthLogin
from configurations.database import get_db
from repositories.users.users_repository import UserRepository
from utilities.auth_utlis import verify_password, generate_tokens, verify_access_token, generate_access_token, \
    verify_refresh_token, security

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

#create department
@router.post("/token", status_code=status.HTTP_201_CREATED)
def user_login_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    try:
        AuthLogin(username=form_data.username, password=form_data.password)

        user_repository = UserRepository(db)
        user = user_repository.get_user_by_email(form_data.username)
        if not user:
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        is_valid = verify_password(form_data.password, user.hashed_password)
        if is_valid:
            return generate_tokens(user)
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid data format {e}"
        )


@router.post("/refresh", status_code=status.HTTP_201_CREATED)
def refresh_access_token(
        authorization: HTTPAuthorizationCredentials = Depends(security),  # Authorization header dependency
        db: Session = Depends(get_db)
):
    refresh_token = authorization.credentials  # Extract token directly
    payload = verify_refresh_token(refresh_token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Fetch user to ensure they still exist
    user_repository = UserRepository(db)
    user = user_repository.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return generate_access_token(user)
