from fastapi import status


class DomainException(Exception):
    def __init__(self, detail: str, code: str, status_code: int) -> None:
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(detail)

    @classmethod
    def unauthorized(cls, detail: str = "Autenticacao invalida ou ausente.") -> "DomainException":
        return cls(detail=detail, code="UNAUTHORIZED", status_code=status.HTTP_401_UNAUTHORIZED)

    @classmethod
    def invalid_google_token(cls) -> "DomainException":
        return cls(
            detail="Token do Google invalido ou expirado.",
            code="INVALID_GOOGLE_TOKEN",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    @classmethod
    def household_required(cls) -> "DomainException":
        return cls(
            detail="Usuario precisa criar ou entrar em uma casa.",
            code="HOUSEHOLD_REQUIRED",
            status_code=status.HTTP_403_FORBIDDEN,
        )

    @classmethod
    def resource_not_found(cls) -> "DomainException":
        return cls(
            detail="Recurso nao encontrado.",
            code="RESOURCE_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @classmethod
    def invite_invalid_or_used(cls) -> "DomainException":
        return cls(
            detail="Token de convite expirado, inexistente ou ja utilizado.",
            code="INVITE_INVALID_OR_USED",
            status_code=status.HTTP_410_GONE,
        )

    @classmethod
    def scan_extraction_failed(cls) -> "DomainException":
        return cls(
            detail="Nao foi possivel extrair os dados da nota. Verifique a qualidade da imagem.",
            code="SCAN_EXTRACTION_FAILED",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @classmethod
    def price_mismatch(cls, detail: str = "Soma dos itens diverge do total da nota.") -> "DomainException":
        return cls(
            detail=detail,
            code="PRICE_MISMATCH",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @classmethod
    def insufficient_stock(cls) -> "DomainException":
        return cls(
            detail="Quantidade insuficiente em estoque.",
            code="INSUFFICIENT_STOCK",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @classmethod
    def conflict(cls, detail: str, code: str = "CONFLICT") -> "DomainException":
        return cls(detail=detail, code=code, status_code=status.HTTP_409_CONFLICT)
