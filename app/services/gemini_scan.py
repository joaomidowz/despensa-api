from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Any

import requests

from app.core.config import get_settings
from app.core.exceptions import DomainException
from app.schemas.receipts import ReceiptScanItemResponse, ReceiptScanResponse

_DATA_URI_PATTERN = re.compile(r"^data:(?P<mime>[\w.+-]+/[\w.+-]+);base64,(?P<data>.+)$", re.DOTALL)
_MEASURE_PATTERN = re.compile(r"^(?P<amount>\d+)(?P<unit>[A-Z]{1,4})$")

_TOKEN_MAP = {
    "MORT": "Mortadela",
    "DEFUM": "Defumada",
    "CAL": "Calabresa",
    "4QU": "Quatro Queijos",
}


def _extract_base64_and_mime(image_base64: str) -> tuple[str, str]:
    content = image_base64.strip()
    match = _DATA_URI_PATTERN.match(content)
    if match:
        return match.group("data"), match.group("mime")
    return content, "image/jpeg"


def _scan_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "market_name": {"type": "string"},
            "receipt_date": {"type": "string"},
            "total_amount": {"type": "number"},
            "items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "raw_name": {"type": "string"},
                        "display_name": {"type": "string"},
                        "quantity": {"type": "number"},
                        "unit_price": {"type": "number"},
                        "discount_amount": {"type": "number"},
                        "total_price": {"type": "number"},
                        "item_type": {"type": "string", "enum": ["PRODUCT", "DISCOUNT"]},
                    },
                    "required": [
                        "raw_name",
                        "quantity",
                        "unit_price",
                        "discount_amount",
                        "total_price",
                        "item_type",
                    ],
                },
            },
        },
        "required": ["market_name", "receipt_date", "total_amount", "items"],
    }


def _build_prompt() -> str:
    return (
        "Leia um cupom fiscal brasileiro e responda apenas JSON valido. "
        "Obrigatorio: market_name, receipt_date, total_amount, items. "
        "Cada item: raw_name, display_name, quantity, unit_price, discount_amount, total_price, item_type. "
        "raw_name = texto cru da nota. "
        "display_name = nome amigavel, expandindo abreviacoes obvias com alta confianca; se houver duvida, repita raw_name. "
        "Use PRODUCT para produto normal. "
        "Use DISCOUNT apenas para desconto global da nota com total_price negativo, quantity 1, unit_price 0 e discount_amount 0. "
        "Se faltar market_name, total_amount ou ao menos 1 item valido, responda JSON invalido para rejeicao. "
        "Nao inclua markdown, comentarios nem texto fora do JSON."
    )


def _humanize_token(token: str, previous_token: str | None, all_tokens: list[str]) -> str:
    upper = token.upper()
    if upper in _TOKEN_MAP:
        return _TOKEN_MAP[upper]
    if upper == "M" and previous_token == "QUEIJO":
        return "Mussarela"
    if upper == "T" and "CAFE" in all_tokens:
        return "Tradicional"

    measure_match = _MEASURE_PATTERN.match(upper)
    if measure_match:
        return f"{measure_match.group('amount')}{measure_match.group('unit').lower()}"
    if upper.isdigit():
        return upper
    return upper.capitalize()


def _build_display_name(raw_name: str) -> str:
    tokens = raw_name.strip().split()
    if not tokens:
        return raw_name.strip()

    upper_tokens = [token.upper() for token in tokens]
    display_tokens: list[str] = []
    previous_token: str | None = None
    for token in upper_tokens:
        display_tokens.append(_humanize_token(token, previous_token, upper_tokens))
        previous_token = token
    return " ".join(display_tokens)


def _extract_text_from_response(payload: dict[str, Any]) -> str:
    try:
        candidates = payload["candidates"]
        parts = candidates[0]["content"]["parts"]
    except (KeyError, IndexError, TypeError) as exc:
        raise DomainException.scan_extraction_failed() from exc

    texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    text = "".join(texts).strip()
    if not text:
        raise DomainException.scan_extraction_failed()
    return text


def _coerce_scan_response(data: dict[str, Any]) -> ReceiptScanResponse:
    try:
        items = [
            ReceiptScanItemResponse(
                raw_name=str(item["raw_name"]).strip(),
                display_name=str(item.get("display_name") or _build_display_name(str(item["raw_name"]))).strip(),
                quantity=Decimal(str(item["quantity"])),
                unit_price=Decimal(str(item["unit_price"])),
                discount_amount=Decimal(str(item.get("discount_amount", 0))),
                total_price=Decimal(str(item["total_price"])),
                item_type=item.get("item_type", "PRODUCT"),
            )
            for item in data["items"]
            if str(item.get("raw_name", "")).strip()
        ]
        response = ReceiptScanResponse(
            market_name=str(data["market_name"]).strip(),
            receipt_date=data["receipt_date"],
            total_amount=Decimal(str(data["total_amount"])),
            items=items,
        )
    except Exception as exc:
        raise DomainException.scan_extraction_failed() from exc

    if not response.market_name or response.total_amount <= 0 or not response.items:
        raise DomainException.scan_extraction_failed()
    return response


def scan_receipt_with_gemini(image_base64: str) -> ReceiptScanResponse:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise DomainException(
            detail="GEMINI_API_KEY nao configurada no ambiente.",
            code="SCAN_PROVIDER_NOT_CONFIGURED",
            status_code=500,
        )

    inline_data, mime_type = _extract_base64_and_mime(image_base64)

    request_body = {
        "contents": [
            {
                "parts": [
                    {"text": _build_prompt()},
                    {"inlineData": {"mimeType": mime_type, "data": inline_data}},
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": _scan_schema(),
        },
    }

    try:
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent",
            headers={
                "x-goog-api-key": settings.gemini_api_key,
                "Content-Type": "application/json",
            },
            json=request_body,
            timeout=60,
        )
    except requests.RequestException as exc:
        raise DomainException.scan_extraction_failed() from exc

    if response.status_code >= 400:
        raise DomainException.scan_extraction_failed()

    try:
        payload = response.json()
        raw_text = _extract_text_from_response(payload)
        data = json.loads(raw_text)
    except Exception as exc:
        raise DomainException.scan_extraction_failed() from exc

    return _coerce_scan_response(data)
