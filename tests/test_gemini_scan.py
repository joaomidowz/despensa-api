from decimal import Decimal
from types import SimpleNamespace

from app.core.exceptions import DomainException
from app.services.gemini_scan import (
    _build_display_name,
    _coerce_scan_response,
    _scan_models_to_try,
    scan_receipt_with_gemini,
)


def test_build_display_name_humanizes_common_receipt_abbreviations():
    assert _build_display_name("QUEIJO M PRESIDENT") == "Queijo Mussarela President"
    assert _build_display_name("MORT SADIA DEFUM 200") == "Mortadela Sadia Defumada 200"
    assert _build_display_name("PIZZA SADIA 460G 4QU") == "Pizza Sadia 460g Quatro Queijos"


def test_coerce_scan_response_fills_display_name_when_missing():
    response = _coerce_scan_response(
        {
            "market_name": "Pedro Muffato e Cia Ltda",
            "receipt_date": "2026-04-02T20:00:55Z",
            "total_amount": 109.24,
            "items": [
                {
                    "raw_name": "QUEIJO M PRESIDENT",
                    "quantity": 1,
                    "unit_price": 7.99,
                    "discount_amount": 0,
                    "total_price": 7.99,
                    "item_type": "PRODUCT",
                }
            ],
        }
    )

    assert response.items[0].raw_name == "QUEIJO M PRESIDENT"
    assert response.items[0].display_name == "Queijo Mussarela President"
    assert response.items[0].total_price == Decimal("7.99")


def test_scan_models_to_try_keeps_primary_and_unique_fallback():
    assert _scan_models_to_try("gemini-2.0-flash-lite", "gemini-2.5-flash") == [
        "gemini-2.0-flash-lite",
        "gemini-2.5-flash",
    ]
    assert _scan_models_to_try("gemini-2.5-flash", "gemini-2.5-flash") == ["gemini-2.5-flash"]


def test_scan_receipt_with_gemini_falls_back_to_second_model(monkeypatch):
    response = _coerce_scan_response(
        {
            "market_name": "Pedro Muffato e Cia Ltda",
            "receipt_date": "2026-04-02T20:00:55Z",
            "total_amount": 109.24,
            "items": [
                {
                    "raw_name": "QUEIJO M PRESIDENT",
                    "display_name": "Queijo Mussarela President",
                    "quantity": 1,
                    "unit_price": 7.99,
                    "discount_amount": 0,
                    "total_price": 7.99,
                    "item_type": "PRODUCT",
                }
            ],
        }
    )
    attempted_models: list[str] = []

    monkeypatch.setattr(
        "app.services.gemini_scan.get_settings",
        lambda: SimpleNamespace(
            gemini_api_key="test-key",
            gemini_model="gemini-2.0-flash-lite",
            gemini_fallback_model="gemini-2.5-flash",
        ),
    )

    def fake_request_scan(model_name: str, api_key: str, request_body: dict):
        attempted_models.append(model_name)
        assert api_key == "test-key"
        assert "contents" in request_body
        if model_name == "gemini-2.0-flash-lite":
            raise DomainException.scan_extraction_failed()
        return response

    monkeypatch.setattr("app.services.gemini_scan._request_scan", fake_request_scan)

    result = scan_receipt_with_gemini("ZmFrZS1pbWFnZQ==")

    assert attempted_models == ["gemini-2.0-flash-lite", "gemini-2.5-flash"]
    assert result.market_name == "Pedro Muffato e Cia Ltda"
