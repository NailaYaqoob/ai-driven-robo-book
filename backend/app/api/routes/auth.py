"""Authentication API routes."""

import uuid
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from app.core.database import get_db
from app.core.security import verify_password, hash_password
from app.core.config import get_settings
from app.models.user import User
from app.models.personalization import UserPreference
from app.schemas.auth import SignupRequest, SigninRequest, TokenResponse, UserResponse, SessionResponse

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()
settings = get_settings()


def create_access_token(user_id: str) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(days=1)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    """Dependency to get current authenticated user from JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(credentials.credentials, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # `sub` is the stringified UUID; cast back so it binds to the UUID column.
    try:
        user_uuid = uuid.UUID(str(user_id))
    except (ValueError, TypeError):
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    return user


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Create a new user account with personalization preferences.

    - **email**: User email address (must be unique)
    - **password**: Password (min 8 characters)
    - **full_name**: Optional full name
    - **persona**: Learning persona (student, educator, self_learner, professional)
    - **skill_level**: Current skill level (beginner, intermediate, advanced)
    - **learning_pace**: Preferred pace (accelerated, standard, extended)
    - **software_background**: Prior software experience
    - **hardware_background**: Hardware access level
    - **learning_goal**: Primary learning objective
    """
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    hashed_password = hash_password(request.password)
    user = User(
        email=request.email,
        password_hash=hashed_password,
        full_name=request.full_name
    )
    db.add(user)
    await db.flush()  # Get user.id before committing

    # Create user preferences
    preference = UserPreference(
        user_id=user.id,
        persona=request.persona,
        skill_level=request.skill_level,
        learning_pace=request.learning_pace,
        language_preference="en",
        software_background=request.software_background,
        hardware_background=request.hardware_background,
        learning_goal=request.learning_goal
    )
    db.add(preference)
    await db.commit()
    await db.refresh(user)

    # Generate access token
    access_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/signin", response_model=TokenResponse)
async def signin(
    request: SigninRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Sign in with email and password.

    - **email**: User email address
    - **password**: User password

    Returns JWT access token valid for 24 hours.
    """
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Generate access token
    access_token = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/session", response_model=SessionResponse)
async def get_session(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Check current session status.

    Returns authenticated user if valid token is provided.
    """
    return SessionResponse(
        authenticated=True,
        user=UserResponse.model_validate(current_user)
    )


@router.post("/signout")
async def signout():
    """
    Sign out (client should delete token).

    Note: JWT tokens cannot be invalidated server-side.
    Client must delete the token from storage.
    """
    return {"message": "Signed out successfully"}
