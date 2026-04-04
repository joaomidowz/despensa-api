from app.schemas.common import ErrorResponse


def error_response(description: str) -> dict:
    return {
        "model": ErrorResponse,
        "description": description,
    }


UNAUTHORIZED_RESPONSE = error_response("Autenticacao invalida ou ausente.")
VALIDATION_ERROR_RESPONSE = error_response("Erro de validacao nos dados enviados.")
HOUSEHOLD_REQUIRED_RESPONSE = error_response(
    "Usuario autenticado precisa criar ou entrar em uma casa."
)
RESOURCE_NOT_FOUND_RESPONSE = error_response(
    "Recurso nao existe ou nao pertence a household autenticada."
)
INVITE_INVALID_OR_USED_RESPONSE = error_response(
    "Token de convite expirado, inexistente ou ja utilizado."
)
PRICE_MISMATCH_RESPONSE = error_response(
    "Matematica do item ou total da nota nao fecha."
)
SCAN_EXTRACTION_FAILED_RESPONSE = error_response(
    "Nao foi possivel extrair os dados obrigatorios da nota."
)
INSUFFICIENT_STOCK_RESPONSE = error_response(
    "Quantidade insuficiente em estoque."
)
ACCOUNT_CONFLICT_RESPONSE = error_response(
    "Ja existe um usuario com este email vinculado a outra conta Google."
)
NOT_IMPLEMENTED_RESPONSE = error_response("Endpoint ainda nao implementado.")

