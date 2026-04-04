from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_household
from app.api.responses import HOUSEHOLD_REQUIRED_RESPONSE, UNAUTHORIZED_RESPONSE
from app.schemas.auth import UserResponse
from app.schemas.shopping_list import ShoppingListCatalogItemResponse
from app.services.shopping_list import list_shopping_list_catalog as list_shopping_list_catalog_service

router = APIRouter(prefix="/shopping-list", tags=["shopping-list"])


@router.get(
    "/catalog",
    response_model=list[ShoppingListCatalogItemResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
    },
)
def list_shopping_list_catalog(
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> list[ShoppingListCatalogItemResponse]:
    return list_shopping_list_catalog_service(db, current_user)
