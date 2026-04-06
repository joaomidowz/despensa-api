from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_current_user_record, get_db_session
from app.api.responses import (
    ACCOUNT_CONFLICT_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.models.user import User
from app.schemas.auth import AuthResponse, GoogleAuthRequest, UserResponse
from app.services.auth import authenticate_with_google

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/google",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        409: ACCOUNT_CONFLICT_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def google_auth(payload: GoogleAuthRequest, db: Session = Depends(get_db_session)) -> AuthResponse:
    return authenticate_with_google(db, payload.google_id_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={401: UNAUTHORIZED_RESPONSE},
)
def get_me(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
    return current_user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: UNAUTHORIZED_RESPONSE},
)
def logout(current_user: User = Depends(get_current_user_record), db: Session = Depends(get_db_session)) -> None:
    current_user.token_version += 1
    db.add(current_user)
    db.commit()
