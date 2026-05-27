"""Personalization API routes."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.models.personalization import UserPreference
from app.schemas.personalization import (
    PersonalizationProfileResponse,
    UpdatePersonalizationRequest,
    LocalStorageSyncRequest
)
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/personalization", tags=["personalization"])


@router.get("/profile", response_model=PersonalizationProfileResponse)
async def get_personalization_profile(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Get current user's personalization preferences.

    Requires authentication. Returns persona, skill level, learning pace, and language preference.
    """
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    preference = result.scalar_one_or_none()

    if not preference:
        # Create default preferences if they don't exist
        preference = UserPreference(user_id=current_user.id)
        db.add(preference)
        await db.commit()
        await db.refresh(preference)

    return PersonalizationProfileResponse.model_validate(preference)


@router.put("/profile", response_model=PersonalizationProfileResponse)
async def update_personalization_profile(
    request: UpdatePersonalizationRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Update user's personalization preferences.

    - **persona**: Update learning persona
    - **skill_level**: Update skill level
    - **learning_pace**: Update learning pace
    - **language_preference**: Change language (en/ur)
    - **software_background**: Update software experience
    - **hardware_background**: Update hardware access
    - **learning_goal**: Update learning objective

    Only provided fields will be updated (partial update).
    """
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    preference = result.scalar_one_or_none()

    if not preference:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personalization profile not found"
        )

    # Update fields if provided
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(preference, field, value)

    await db.commit()
    await db.refresh(preference)

    return PersonalizationProfileResponse.model_validate(preference)


@router.post("/sync-from-localStorage", response_model=PersonalizationProfileResponse)
async def sync_from_local_storage(
    request: LocalStorageSyncRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Sync personalization preferences from localStorage to backend on login.

    When a user sets preferences while not logged in (stored in localStorage),
    this endpoint syncs those preferences to the backend upon authentication.

    This ensures preferences persist across devices after login.
    """
    result = await db.execute(
        select(UserPreference).where(UserPreference.user_id == current_user.id)
    )
    preference = result.scalar_one_or_none()

    if not preference:
        preference = UserPreference(user_id=current_user.id)
        db.add(preference)

    # Sync from localStorage
    if request.persona:
        preference.persona = request.persona
    if request.skill_level:
        preference.skill_level = request.skill_level
    if request.learning_pace:
        preference.learning_pace = request.learning_pace
    if request.language_preference:
        preference.language_preference = request.language_preference

    await db.commit()
    await db.refresh(preference)

    return PersonalizationProfileResponse.model_validate(preference)
