from fastapi import APIRouter, Query, Response, status

from app.api.responses import (
    HOUSEHOLD_REQUIRED_RESPONSE,
    INSUFFICIENT_STOCK_RESPONSE,
    NOT_IMPLEMENTED_RESPONSE,
    RESOURCE_NOT_FOUND_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.core.exceptions import DomainException
from app.schemas.inventory import (
    CreateInventoryItemRequest,
    CreateInventoryItemResponse,
    InventoryAmountRequest,
    InventoryAmountResponse,
    InventoryItemResponse,
    UpdateInventoryItemRequest,
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
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def list_inventory(status_filter: str | None = Query(default=None, alias="status")) -> list[InventoryItemResponse]:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.post(
    "",
    response_model=CreateInventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def create_inventory_item(payload: CreateInventoryItemRequest) -> CreateInventoryItemResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


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
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def consume_inventory_item(inventory_id: str, payload: InventoryAmountRequest) -> InventoryAmountResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.patch(
    "/{inventory_id}/add",
    response_model=InventoryAmountResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def add_inventory_item(inventory_id: str, payload: InventoryAmountRequest) -> InventoryAmountResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.put(
    "/{inventory_id}",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def update_inventory_item(inventory_id: str, payload: UpdateInventoryItemRequest) -> InventoryItemResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.delete(
    "/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def delete_inventory_item(inventory_id: str) -> Response:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)
