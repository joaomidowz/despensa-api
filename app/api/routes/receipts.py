from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session, require_household
from app.api.responses import (
    ACCOUNT_CONFLICT_RESPONSE,
    HOUSEHOLD_REQUIRED_RESPONSE,
    PRICE_MISMATCH_RESPONSE,
    RESOURCE_NOT_FOUND_RESPONSE,
    SCAN_EXTRACTION_FAILED_RESPONSE,
    UNAUTHORIZED_RESPONSE,
    VALIDATION_ERROR_RESPONSE,
)
from app.schemas.auth import UserResponse
from app.schemas.receipts import (
    ConfirmReceiptRequest,
    ConfirmReceiptResponse,
    PaginatedReceiptsResponse,
    ReconcileShoppingListRequest,
    ReconcileShoppingListResponse,
    ReceiptDetailResponse,
    ReceiptScanRequest,
    ReceiptScanResponse,
    UpdateReceiptResponse,
)
from app.services.receipts import (
    confirm_receipt as confirm_receipt_service,
    get_receipt_detail as get_receipt_detail_service,
    list_receipts as list_receipts_service,
    reconcile_shopping_list_items as reconcile_shopping_list_items_service,
    update_receipt as update_receipt_service,
)
from app.services.gemini_scan import scan_receipt_with_gemini

router = APIRouter(prefix="/receipts", tags=["receipts"])


@router.post(
    "/scan",
    response_model=ReceiptScanResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: SCAN_EXTRACTION_FAILED_RESPONSE,
    },
)
def scan_receipt(
    payload: ReceiptScanRequest,
    current_user: UserResponse = Depends(require_household),
) -> ReceiptScanResponse:
    _ = current_user
    return scan_receipt_with_gemini(payload.image_base64)


@router.post(
    "/reconcile-shopping-list",
    response_model=ReconcileShoppingListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def reconcile_shopping_list(
    payload: ReconcileShoppingListRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> ReconcileShoppingListResponse:
    return reconcile_shopping_list_items_service(db, current_user, payload)


@router.post(
    "",
    response_model=ConfirmReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: PRICE_MISMATCH_RESPONSE,
    },
)
def confirm_receipt(
    payload: ConfirmReceiptRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> ConfirmReceiptResponse:
    return confirm_receipt_service(db, current_user, payload)


@router.put(
    "/{receipt_id}",
    response_model=UpdateReceiptResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
        409: ACCOUNT_CONFLICT_RESPONSE,
        422: PRICE_MISMATCH_RESPONSE,
    },
)
def update_receipt(
    receipt_id: UUID,
    payload: ConfirmReceiptRequest,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> UpdateReceiptResponse:
    return update_receipt_service(db, current_user, receipt_id, payload)


@router.get(
    "",
    response_model=PaginatedReceiptsResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        422: VALIDATION_ERROR_RESPONSE,
    },
)
def list_receipts(
    month: int | None = Query(default=None, ge=1, le=12),
    year: int | None = Query(default=None, ge=2000),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> PaginatedReceiptsResponse:
    return list_receipts_service(db, current_user, month, year, limit, offset)


@router.get(
    "/{receipt_id}",
    response_model=ReceiptDetailResponse,
    status_code=status.HTTP_200_OK,
    responses={
        401: UNAUTHORIZED_RESPONSE,
        403: HOUSEHOLD_REQUIRED_RESPONSE,
        404: RESOURCE_NOT_FOUND_RESPONSE,
    },
)
def get_receipt_detail(
    receipt_id: UUID,
    current_user: UserResponse = Depends(require_household),
    db: Session = Depends(get_db_session),
) -> ReceiptDetailResponse:
    return get_receipt_detail_service(db, current_user, receipt_id)
