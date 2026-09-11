# Project Constitution (gemini.md)

## Data Schemas
**Input Payload (From Supplier API / Airtable):**
```json
{
  "product_id": "string",
  "title": "string",
  "description_html": "string",
  "supplier_cost": "float",
  "recommended_price": "float",
  "images": ["url_string"],
  "shipping_time_days": "integer",
  "rating": "float"
}
```

**Output Payload (To Shopify API):**
```json
{
  "product": {
    "title": "string",
    "body_html": "string",
    "vendor": "string",
    "product_type": "Pet Tech",
    "status": "draft",
    "variants": [
      {
        "price": "float (supplier_cost * 2.5)",
        "inventory_management": "shopify"
      }
    ],
    "images": [
      { "src": "url_string" }
    ]
  }
}
```

## Behavioral Rules
- **Rule 1:** Never guess at business logic.
- **Rule 2:** Only import products with `rating` >= 4.5.
- **Rule 3:** Only import products with `shipping_time_days` <= 10.
- **Rule 4:** Automatically calculate variant price for a minimum 40% margin (e.g., 2.5x markup).
- Follow the A.N.T. 3-layer architecture (Architecture, Navigation, Tools).
- Self-Annealing Loop: Analyze, Patch, Test, Update Architecture.

## Architectural Invariants
- `architecture/`: Layer 1 (Technical SOPs)
- `tools/`: Layer 3 (Deterministic Python scripts)
- `.tmp/`: Ephemeral local storage
- `gemini.md` is law.
