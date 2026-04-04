from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_household
from app.api.responses import (
    HOUSEHOLD_REQUIRED_RESPONSE,
    INSUFFICIENT_STOCK_RESPONSE,
    RESOURCE_NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.schemas.auth import UserResponse
from app.schemas.inventory import (
    CreateInventoryItemRequest,
    CreateInventoryItemResponse,
    InventoryAmountRequest,
    InventoryAmountResponse,
    InventoryItemResponse,
    UpdateInventoryItemRequest,
)
from app.services.inventory import (
    add_inventory_item as add_inventory_item_service,
    consume_inventory_item as consume_inventory_item_service,
    create_inventory_item as create_inventory_item_service,
    delete_inventory_item as delete_inventory_item_service,
    list_inventory as list_inventory_service,
    update_inventory_item as update_inventory_item_service,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get(
    "",
    response_model=list[InventoryItemResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def list_inventory(
    status_filter: str | None = Query(default=None, alias="status"),
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> list[InventoryItemResponse]:
    return list_inventory_service(db, current_user, status_filter)


@router.post(
    "",
    response_model=CreateInventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def create_inventory_item(
    payload: CreateInventoryItemRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> CreateInventoryItemResponse:
    return create_inventory_item_service(db, current_user, payload)


@router.patch(
    "/{inventory_id}/consume",
    response_model=InventoryAmountResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: INSUFFICIENT_STOCK_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def consume_inventory_item(
    inventory_id: UUID,
    payload: InventoryAmountRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> InventoryAmountResponse:
    return consume_inventory_item_service(db, current_user, inventory_id, payload.amount)


@router.patch(
    "/{inventory_id}/add",
    response_model=InventoryAmountResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def add_inventory_item(
    inventory_id: UUID,
    payload: InventoryAmountRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> InventoryAmountResponse:
    return add_inventory_item_service(db, current_user, inventory_id, payload.amount)


@router.put(
    "/{inventory_id}",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def update_inventory_item(
    inventory_id: UUID,
    payload: UpdateInventoryItemRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> InventoryItemResponse:
    return update_inventory_item_service(db, current_user, inventory_id, payload)


@router.delete(
    "/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
    },
)
def delete_inventory_item(
    inventory_id: UUID,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> Response:
    delete_inventory_item_service(db, current_user, inventory_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
