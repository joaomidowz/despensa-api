from decimal import Decimal

from app.services.gemini_scan import _build_display_name, _coerce_scan_response


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
