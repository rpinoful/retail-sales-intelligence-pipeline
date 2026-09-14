from pathlib import Path


REQUIRED_COLUMNS: dict[str, list[str]] = {
    "products": [
        "product_id",
        "product_name",
        "category",
        "unit_cost_brl",
        "supplier_currency",
        "active",
    ],
    "stores": [
        "store_id",
        "store_name",
        "city",
        "state",
        "channel",
    ],
    "fixed_costs": [
        "month",
        "store_id",
        "rent_brl",
        "payroll_brl",
        "utilities_brl",
        "other_costs_brl",
    ],
    "sales": [
        "sale_id",
        "sale_date",
        "store_id",
        "product_id",
        "quantity",
        "unit_price_brl",
        "discount_pct",
        "payment_method",
    ],
}

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_EXCEL_PATH = PROJECT_ROOT / "data" / "raw" / "excel" / "store_operations.xlsx"

BRONZE_PATH = PROJECT_ROOT / "data" / "bronze"
SILVER_PATH = PROJECT_ROOT / "data" / "silver"
GOLD_PATH = PROJECT_ROOT / "data" / "gold"