from datetime import timedelta, datetime
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from dotenv import load_dotenv
import os

from starlette import status

# Load environment variables
load_dotenv()

security = HTTPBearer()

# Constants
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_MINUTES = float(os.getenv("REFRESH_TOKEN_EXPIRE_HOURS", "1440"))
JWT_ACCESS_SECRET = os.getenv("JWT_ACCESS_SECRET")
JWT_REFRESH_SECRET = os.getenv("JWT_REFRESH_SECRET")

# Validate secrets
if not JWT_ACCESS_SECRET or not JWT_REFRESH_SECRET:
    raise ValueError("JWT secret keys must be set in the environment variables")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
oauth2_refresh_scheme = OAuth2PasswordBearer(tokenUrl="/auth/refresh")


# Password hashing functions
def get_password_hash(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Token generation functions
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, JWT_ACCESS_SECRET, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, JWT_REFRESH_SECRET, algorithm=ALGORITHM)


# Token verification functions
def verify_access_token(token: str = Depends(oauth2_scheme)) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_ACCESS_SECRET, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def verify_refresh_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_REFRESH_SECRET, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


def generate_tokens(user):
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "roles": [role["name"] for role in user.roles],
            "permissions": user.permissions if hasattr(user, "permissions") else []
        }
    )

    refresh_token = create_refresh_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }


def generate_access_token(user):
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "roles": [role["name"] for role in user.roles],
            "permissions": user.permissions if hasattr(user, "permissions") else []
        }
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer"
    }
