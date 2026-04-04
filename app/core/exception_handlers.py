from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import DomainException


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def handle_request_validation_error(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Erro de validacao nos dados enviados.",
                "code": "VALIDATION_ERROR",
            },
        )

    @app.exception_handler(DomainException)
    async def handle_domain_exception(
        request: Request,
        exc: DomainException,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "code": exc.code},
        )

    @app.exception_handler(NotImplementedError)
    async def handle_not_implemented(
        request: Request,
        exc: NotImplementedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content={"detail": str(exc), "code": "NOT_IMPLEMENTED"},
        )

