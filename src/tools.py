"""Tools the LLM can call (function calling).

Each function's docstring becomes the tool description sent to the model,
so it explains WHEN to use each one. Customer-facing values stay in
Portuguese because the store serves Brazilian customers.
"""
from datetime import date

from src.data_loader import load_orders, load_products, normalize
from src.policies import load_sections

SHOW_CALLS = False  # turned on by the CLI --debug flag

PRODUCT_STATUS = {
    "active": "ativo no catálogo",
    "discontinued": "descontinuado (não faz mais parte do catálogo)",
    "coming_soon": "em breve (ainda não está à venda)",
}
ORDER_STATUS = {
    "pending": "aguardando confirmação do pagamento",
    "confirmed": "pagamento confirmado, em separação",
    "shipped": "enviado",
    "delivered": "entregue",
    "cancelled": "cancelado",
}
PAYMENT_METHODS = {
    "pix": "PIX",
    "debit": "cartão de débito",
    "boleto": "boleto bancário",
    "credit_3x": "cartão de crédito em 3x",
    "credit_6x": "cartão de crédito em 6x",
    "credit_12x": "cartão de crédito em 12x",
}


def _log(name: str, **args):
    if SHOW_CALLS:
        print(f"  [tool] {name}({args})")


def _format_product(p) -> dict:
    product = {
        "name": p["name"],
        "category": p["category_name"],
        "price": float(p["price_brl"]),
        "status": PRODUCT_STATUS.get(p["status"], p["status"]),
        "stock": int(p["stock_quantity"]),
        "available_for_purchase": bool(p["available"]),
        "description": p["description"],
        "specifications": p["specs"],
    }
    if p["discount_percent"] > 0:
        product["active_promotion"] = {
            "name": p["promotion"],
            "discount_percent": int(p["discount_percent"]),
            "promotional_price": float(p["final_price"]),
        }
    return product


def search_products(
    term: str = "",
    category: str = "",
    max_price: float = 0,
    min_price: float = 0,
    only_available: bool = False,
) -> dict:
    """Searches the instrument catalog with real-time price, stock and promotions.

    ALWAYS use it when the customer asks about price, availability, stock or
    promotion of a product, or asks for instrument suggestions.

    Args:
        term: brand, model or feature (e.g. "takamine gd20", "nylon", "eletrico", "7 cordas"). Empty = no filter.
        category: one of: Guitarras, Baixos, Baterias e Percussão, Teclados e Pianos, Violões, Ukuleles. Empty = all.
        max_price: maximum final price in BRL (0 = no limit).
        min_price: minimum final price in BRL (0 = no limit).
        only_available: True to return only products that can be bought now.
    """
    _log("search_products", term=term, category=category, max_price=max_price,
         min_price=min_price, only_available=only_available)
    df = load_products()

    if category:
        df = df[df["category_name"].apply(normalize) == normalize(category)]
    if term:
        # score each product by how many words match and keep the best ones
        words = normalize(term).split()
        scores = df["search_text"].apply(lambda text: sum(w in text for w in words))
        df = df[(scores > 0) & (scores == scores.max())]
    if max_price:
        df = df[df["final_price"] <= max_price]
    if min_price:
        df = df[df["final_price"] >= min_price]
    if only_available:
        df = df[df["available"]]

    if df.empty:
        return {"found": 0, "products": []}
    df = df.sort_values("final_price")
    return {
        "found": len(df),
        "products": [_format_product(p) for _, p in df.head(10).iterrows()],
    }


def get_order(order_id: int, email: str) -> dict:
    """Gets status, tracking, items and dates of an order.

    For security (LGPD, Brazilian data protection law) it requires the order
    number AND the e-mail used in the purchase. Ask the customer for both
    before calling. Also use it to evaluate exchanges and returns (it returns
    how many days have passed since delivery).

    Args:
        order_id: order number given by the customer.
        email: customer e-mail registered in the order.
    """
    _log("get_order", order_id=order_id, email=email)
    orders, customers, items = load_orders()

    order = orders[orders["order_id"] == int(order_id)]
    customer = customers[customers["customer_id"].isin(order["customer_id"])]
    # same message for "not found" and "wrong e-mail": does not reveal whether the order exists
    if order.empty or normalize(customer.iloc[0]["email"]) != normalize(email):
        return {"error": "Não encontrei pedido com esse número e e-mail."}

    order, customer = order.iloc[0], customer.iloc[0]
    order_items = items[items["order_id"] == order["order_id"]]
    result = {
        "order_id": int(order["order_id"]),
        "customer_first_name": customer["name"].split()[0],
        "order_date": order["order_date"],
        "status": ORDER_STATUS.get(order["status"], order["status"]),
        "total_brl": float(order["total_brl"]),
        "payment_method": PAYMENT_METHODS.get(order["payment_method"], order["payment_method"]),
        "items": [f"{int(i['quantity'])}x {i['name']}" for _, i in order_items.iterrows()],
        "tracking_code": order["tracking_code"] or None,
        "estimated_delivery": order["estimated_delivery"] or None,
        "notes": order["notes"] or None,
    }
    if order["status"] == "delivered" and order["estimated_delivery"]:
        delivery = date.fromisoformat(order["estimated_delivery"])
        result["days_since_delivery"] = (date.today() - delivery).days
        result["warning"] = "Actual delivery date is not recorded; the estimated delivery date was used instead."
    return result


def get_policy(topic: str) -> str:
    """Returns the official excerpt of the store policy manual about a topic.

    Use it for rules and store information. Never answer these from memory.

    Args:
        topic: one of: about (address, phone, e-mail, what the store sells), hours,
            payment (methods and installments), returns (returns, regret, defects, exchanges),
            shipping (deliveries, deadlines, tracking), promotions (discount rules),
            customer_service (guidelines and special situations), warranty, privacy (LGPD).
    """
    _log("get_policy", topic=topic)
    sections = load_sections()
    topic = normalize(topic)
    for key, text in sections.items():
        if key.startswith(topic) or topic.startswith(key):
            return text
    return f"Topic not found. Valid topics: {', '.join(sections)}"


TOOLS = [search_products, get_order, get_policy]
