from datetime import datetime, timedelta, timezone
from typing import Optional, List

import bcrypt
from jose import jwt, JWTError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database.session import get_policy_db
from app.models import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt directly.
    Does NOT use Passlib.
    """

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(
        password_bytes,
        salt
    )

    return hashed.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a password using bcrypt directly.
    """

    try:

        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    except Exception:

        return False


# ============================================================
# JWT ACCESS TOKEN
# ============================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta
        or timedelta(
            minutes=settings.JWT_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


# ============================================================
# CURRENT USER
# ============================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    policy_db: Session = Depends(get_policy_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="INVALID_CREDENTIALS",
        headers={
            "WWW-Authenticate": "Bearer"
        },
    )

    try:

        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[
                settings.JWT_ALGORITHM
            ]
        )

        username: str = payload.get("sub")

        if username is None:
            raise credentials_exception

    except JWTError:

        raise credentials_exception

    user = (
        policy_db
        .query(User)
        .filter(
            User.username == username
        )
        .first()
    )

    if user is None or not user.is_active:

        raise credentials_exception

    return user


# ============================================================
# ROLE-BASED AUTHORIZATION
# ============================================================

def require_role(
    allowed_roles: List[str]
):

    def role_checker(
        current_user: User = Depends(
            get_current_user
        )
    ) -> User:

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="ACCESS_DENIED"
            )

        return current_user

    return role_checker