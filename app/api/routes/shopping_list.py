from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_household
from app.api.responses import (
    HOUSEHOLD_REQUIRED_RESPONSE,
    RESOURCE_NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.schemas.auth import UserResponse
from app.schemas.shopping_list import (
    AddInventoryItemToShoppingListRequest,
    CreateShoppingListItemRequest,
    ShoppingListCatalogItemResponse,
    ShoppingListItemResponse,
    UpdateShoppingListItemRequest,
)
from app.services.shopping_list import (
    add_inventory_item_to_shopping_list as add_inventory_item_to_shopping_list_service,
    create_shopping_list_item as create_shopping_list_item_service,
    delete_shopping_list_item as delete_shopping_list_item_service,
    list_shopping_list_catalog as list_shopping_list_catalog_service,
    list_shopping_list_items as list_shopping_list_items_service,
    update_shopping_list_item as update_shopping_list_item_service,
)

router = APIRouter(prefix="/shopping-list", tags=["shopping-list"])


@router.get(
    "/items",
    response_model=list[ShoppingListItemResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
    },
)
def list_shopping_list_items(
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> list[ShoppingListItemResponse]:
    return list_shopping_list_items_service(db, current_user)


@router.post(
    "/items",
    response_model=ShoppingListItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def create_shopping_list_item(
    payload: CreateShoppingListItemRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> ShoppingListItemResponse:
    return create_shopping_list_item_service(db, current_user, payload)


@router.post(
    "/items/from-inventory",
    response_model=ShoppingListItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def add_inventory_item_to_shopping_list(
    payload: AddInventoryItemToShoppingListRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> ShoppingListItemResponse:
    return add_inventory_item_to_shopping_list_service(db, current_user, payload)


@router.patch(
    "/items/{shopping_list_item_id}",
    response_model=ShoppingListItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def update_shopping_list_item(
    shopping_list_item_id: UUID,
    payload: UpdateShoppingListItemRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> ShoppingListItemResponse:
    return update_shopping_list_item_service(db, current_user, shopping_list_item_id, payload)


@router.delete(
    "/items/{shopping_list_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
    },
)
def delete_shopping_list_item(
    shopping_list_item_id: UUID,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> Response:
    delete_shopping_list_item_service(db, current_user, shopping_list_item_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


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
