from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_household
from app.api.responses import HOUSEHOLD_REQUIRED_RESPONSE, UNAUTHORIZED_RESPONSE
from app.schemas.auth import UserResponse
from app.schemas.overview import OverviewResponse
from app.services.overview import get_overview as get_overview_service

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get(
    "",
    response_model=OverviewResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
    },
)
def get_overview(
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> OverviewResponse:
    return get_overview_service(db, current_user)
