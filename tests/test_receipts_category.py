from app.services.receipts import infer_product_category


def test_infer_product_category_uses_receipt_name_keywords():
    assert infer_product_category("Mortadela Sadia Defumada 200g") == "Frios"
    assert infer_product_category("Queijo Mussarela President") == "Laticinios"
    assert infer_product_category("Leite Integral 1L") == "Laticinios"
    assert infer_product_category("Carne Moida Bovina") == "Carnes"
    assert infer_product_category("Pizza Sadia Calabresa 460g") == "Congelados"


def test_infer_product_category_falls_back_when_unknown():
    assert infer_product_category("Produto Xpto Sem Padrao") == "Sem Categoria"
