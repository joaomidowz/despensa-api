# Instrucoes Para Scan De Cupom Fiscal

Use estas instrucoes no Gemini para testar manualmente a extracao de um cupom fiscal brasileiro.

## Objetivo

Extraia os dados de um cupom fiscal brasileiro e devolva somente um JSON valido.

## Regras

- Responda apenas com JSON puro.
- Nao use markdown.
- Nao adicione comentarios.
- Nao adicione texto antes ou depois do JSON.
- Se nao conseguir identificar `market_name`, `total_amount` ou pelo menos 1 item valido, retorne um JSON invalido.

## Campos obrigatorios no JSON

```json
{
  "market_name": "string",
  "receipt_date": "string",
  "total_amount": 0,
  "items": [
    {
      "raw_name": "string",
      "display_name": "string",
      "quantity": 0,
      "unit_price": 0,
      "discount_amount": 0,
      "total_price": 0,
      "item_type": "PRODUCT"
    }
  ]
}
```

## Regras dos itens

- Use `item_type: "PRODUCT"` para produtos normais.
- Use `item_type: "DISCOUNT"` apenas para desconto global da nota.
- Para `DISCOUNT`:
- `raw_name`: descricao do desconto
- `display_name`: versao amigavel para exibicao
  - `quantity`: `1`
  - `unit_price`: `0`
  - `discount_amount`: `0`
  - `total_price`: valor negativo

## Regras de interpretacao

- `market_name`: nome do mercado ou estabelecimento.
- `receipt_date`: data encontrada na nota em formato de texto.
- `total_amount`: total final pago na nota.
- `raw_name`: nome do item como aparece na nota.
- `display_name`: nome amigavel para humanos. Expanda abreviacoes obvias quando houver alta confianca, sem inventar informacao ausente. Se nao tiver confianca, repita `raw_name`.
- `quantity`: quantidade comprada.
- `unit_price`: preco unitario.
- `discount_amount`: desconto do item, se existir. Caso contrario, `0`.
- `total_price`: total daquele item.

## Prompt pronto para colar

```text
Leia um cupom fiscal brasileiro e responda apenas JSON valido. Obrigatorio: market_name, receipt_date, total_amount, items. Cada item: raw_name, display_name, quantity, unit_price, discount_amount, total_price, item_type. raw_name = texto cru da nota. display_name = nome amigavel, expandindo abreviacoes obvias com alta confianca; se houver duvida, repita raw_name. Use PRODUCT para produto normal. Use DISCOUNT apenas para desconto global da nota com total_price negativo, quantity 1, unit_price 0 e discount_amount 0. Se faltar market_name, total_amount ou ao menos 1 item valido, responda JSON invalido para rejeicao. Nao inclua markdown, comentarios nem texto fora do JSON.
```

## Modelo recomendado

Use `gemini-2.0-flash-lite` para testes economicos.
