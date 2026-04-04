from fastapi import APIRouter, Query, status

from app.api.responses import (
    HOUSEHOLD_REQUIRED_RESPONSE,
    NOT_IMPLEMENTED_RESPONSE,
    PRICE_MISMATCH_RESPONSE,
    RESOURCE_NOT_FOUND_RESPONSE,
    SCAN_EXTRACTION_FAILED_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.core.exceptions import DomainException
from app.schemas.receipts import (
    ConfirmReceiptRequest,
    ConfirmReceiptResponse,
    PaginatedReceiptsResponse,
    ReceiptDetailResponse,
    ReceiptScanRequest,
    ReceiptScanResponse,
)

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post(
    "/scan",
    response_model=ReceiptScanResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: SCAN_EXTRACTION_FAILED_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def scan_receipt(payload: ReceiptScanRequest) -> ReceiptScanResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.post(
    "",
    response_model=ConfirmReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: PRICE_MISMATCH_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def confirm_receipt(payload: ConfirmReceiptRequest) -> ConfirmReceiptResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.get(
    "",
    response_model=PaginatedReceiptsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def list_receipts(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PaginatedReceiptsResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)


@router.get(
    "/{receipt_id}",
    response_model=ReceiptDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        501: NOT_IMPLEMENTED_RESPONSE,
    },
)
def get_receipt_detail(receipt_id: str) -> ReceiptDetailResponse:
    raise DomainException("Endpoint ainda nao implementado.", "NOT_IMPLEMENTED", status.HTTP_501_NOT_IMPLEMENTED)
