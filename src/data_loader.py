"""Loads and cleans the store CSV files."""
import json
import unicodedata
from functools import lru_cache

import pandas as pd

from src.config import DATA_DIR

FILE_PREFIX = "desafio_tecnico_ai_eng - "


def normalize(text) -> str:
    """Lowercase without accents, for tolerant search ('violao' matches 'Violão')."""
    text = unicodedata.normalize("NFKD", str(text))
    return "".join(c for c in text if not unicodedata.combining(c)).lower().strip()


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{FILE_PREFIX}{name}.csv", encoding="utf-8")


@lru_cache(maxsize=1)
def load_products() -> pd.DataFrame:
    """Products + category name + active promotion + final price."""
    products = _read("products")
    categories = _read("categories").rename(columns={"name": "category_name"})
    promotions = _read("promotions")

    # active promotions only; if a product has more than one, keep the biggest discount
    active = (
        promotions[promotions["is_active"] == 1]
        .sort_values("discount_percent", ascending=False)
        .drop_duplicates("product_id")
        .rename(columns={"description": "promotion"})
        [["product_id", "discount_percent", "promotion"]]
    )

    df = products.merge(categories[["category_id", "category_name"]], on="category_id", how="left")
    df = df.merge(active, on="product_id", how="left")

    df["discount_percent"] = df["discount_percent"].fillna(0)
    df["final_price"] = (df["price_brl"] * (1 - df["discount_percent"] / 100)).round(2)
    df["available"] = (df["status"] == "active") & (df["stock_quantity"] > 0)
    df["specs"] = df["specs"].apply(lambda s: json.loads(s) if isinstance(s, str) else {})
    # single normalized text used by the keyword search
    df["search_text"] = (df["name"] + " " + df["category_name"] + " " + df["description"]).apply(normalize)
    return df


@lru_cache(maxsize=1)
def load_orders() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (orders, customers, order items with product name)."""
    orders = _read("orders").fillna("")
    customers = _read("customers")
    items = _read("order_items").merge(_read("products")[["product_id", "name"]], on="product_id", how="left")
    return orders, customers, items
