"""Tools the Campus Customs agent can call.

Every fact the agent is allowed to state about a product — its price, its colours, whether
a size is left — comes from one of these functions, which read `data/campus_customs.db`
directly. Nothing here writes to the database.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

from models import ProductDetail, ProductSummary, SearchResults, SizeStock, StockAnswer

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

# Words that match almost everything in a Yale apparel shop, so they add no signal.
STOPWORDS = {
    "a", "an", "and", "any", "are", "do", "does", "for", "got", "has", "have", "in", "is",
    "it", "me", "my", "of", "on", "or", "s", "show", "something", "the", "to", "want",
    "what", "with", "you", "your", "yale", "campus", "customs",
}


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def _stock_by_size(con: sqlite3.Connection, product_id: str) -> dict[str, int]:
    rows = con.execute(
        "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
    ).fetchall()
    return {r["size"]: r["quantity"] for r in rows}


def _summary(row: sqlite3.Row, stock: dict[str, int]) -> ProductSummary:
    ordered = [s for s in SIZE_ORDER if s in stock]
    return ProductSummary(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        price=row["price"],
        sizes_in_stock=[s for s in ordered if stock[s] > 0],
        sizes_sold_out=[s for s in ordered if stock[s] == 0],
        total_stock=sum(stock.values()),
    )


def _score(row: sqlite3.Row, terms: list[str]) -> int:
    """Rank a catalogue row against the shopper's words.

    Weighted by where a term lands: the hand-written search_tags and the product name are
    stronger evidence of intent than a passing mention in the description.
    """
    name = row["name"].lower()
    tags = row["search_tags"].lower()
    colors = row["colors"].lower()
    garment = row["garment_type"].lower()
    description = row["description"].lower()

    score = 0
    for term in terms:
        if term in name:
            score += 5
        if term in tags:
            score += 4
        if term in garment:
            score += 3
        if term in colors:
            score += 2
        if term in description:
            score += 1
    return score


def search_catalogue(
    query: str,
    limit: int = 6,
    max_price: float | None = None,
    min_price: float | None = None,
    in_stock_only: bool = False,
) -> SearchResults:
    """Find products matching a shopper's words, with optional price and stock filters.

    Searches the product name, garment type, colours, description and the hand-written
    search tags.

    Use `max_price` / `min_price` for budget questions ("anything under $40") rather than
    filtering the results yourself — the filter runs over the whole catalogue, so the
    `total_matches` you get back is the real number of items in that range.

    Use `in_stock_only=True` when recommending something the shopper could actually buy
    today, so sold-out items are left out before they reach you.

    Two counts come back and they mean different things. `total_matches` is how many
    products matched your words *and* the filters. `total_in_filters` is how many satisfy
    the filters alone. For a pure budget question ("what is under $40?") quote
    `total_in_filters`, or pass an empty query so the two agree.
    """
    terms = [t for t in re.findall(r"[a-z0-9-]+", query.lower()) if t not in STOPWORDS]
    limit = max(1, min(limit, 12))

    with _connect() as con:
        rows = con.execute("SELECT * FROM catalogue").fetchall()
        stock = {r["product_id"]: _stock_by_size(con, r["product_id"]) for r in rows}

        def keep(row: sqlite3.Row) -> bool:
            if max_price is not None and row["price"] > max_price:
                return False
            if min_price is not None and row["price"] < min_price:
                return False
            if in_stock_only and sum(stock[row["product_id"]].values()) == 0:
                return False
            return True

        eligible = [r for r in rows if keep(r)]

        # No usable search words (e.g. "what do you have?") — the filters alone define the
        # match set, so everything eligible counts.
        if not terms:
            matched = eligible
        else:
            ranked = sorted(
                ((_score(r, terms), r["name"], r) for r in eligible),
                key=lambda item: (-item[0], item[1]),
            )
            matched = [r for score, _, r in ranked if score > 0]

        notes = []
        if min_price is not None:
            notes.append(f"at least ${min_price:g}")
        if max_price is not None:
            notes.append(f"under ${max_price:g}")
        if in_stock_only:
            notes.append("in stock")

        chosen = matched[:limit]
        return SearchResults(
            total_matches=len(matched),
            # The filters on their own. Without this the agent cannot tell "13 matched my
            # words" from "13 exist under $40", and it conflated the two.
            total_in_filters=len(eligible),
            showing=len(chosen),
            products=[_summary(r, stock[r["product_id"]]) for r in chosen],
            filters_applied=", ".join(notes) or None,
        )


def get_product(product_id: str) -> ProductDetail | None:
    """Look up one product by its product_id, including stock for every size.

    Returns None when no product has that id — say so plainly rather than guessing at a
    near match.
    """
    with _connect() as con:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return None
        by_size = _stock_by_size(con, product_id)

    sizes = [
        SizeStock(size=s, quantity=by_size[s], in_stock=by_size[s] > 0)
        for s in SIZE_ORDER
        if s in by_size
    ]
    return ProductDetail(**_summary(row, by_size).model_dump(), sizes=sizes)


def check_stock(product_id: str, size: str) -> StockAnswer:
    """Check whether one product is available in one size.

    Call this before telling a shopper their size is available. `size` is one of
    XS, S, M, L, XL, XXL. When the size is sold out the answer also lists the sizes that
    are available, so an alternative can be offered in the same breath.
    """
    wanted = size.strip().upper()
    with _connect() as con:
        row = con.execute(
            "SELECT name FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            return StockAnswer(
                product_id=product_id, size=wanted, found=False,
                reason="We have no product with that id.",
            )
        by_size = _stock_by_size(con, product_id)

    available = [s for s in SIZE_ORDER if by_size.get(s, 0) > 0]
    if wanted not in by_size:
        return StockAnswer(
            product_id=product_id, product_name=row["name"], size=wanted, found=False,
            reason=(
                "We do not stock that size. This item comes in "
                f"{', '.join(s for s in SIZE_ORDER if s in by_size)}."
            ),
            sizes_in_stock=available,
        )

    quantity = by_size[wanted]
    return StockAnswer(
        product_id=product_id,
        product_name=row["name"],
        size=wanted,
        found=True,
        quantity=quantity,
        in_stock=quantity > 0,
        sizes_in_stock=available,
    )


def unverified_prices(reply: str) -> list[str]:
    """Return any dollar figures in a reply that match no price in the catalogue.

    A backstop for the honesty rules, not a gate: the prompt tells the agent to look prices
    up and the product cards are built from database rows, but this catches a figure that
    was typed into the prose rather than read from a tool. The chat route logs whatever it
    returns; it never blocks a reply, because a legitimate total or price range would also
    land here.
    """
    quoted = re.findall(r"\$\s?(\d+(?:\.\d{1,2})?)", reply)
    if not quoted:
        return []

    with _connect() as con:
        known = {row[0] for row in con.execute("SELECT DISTINCT price FROM catalogue")}

    return [f"${q}" for q in quoted if float(q) not in known]


def unknown_product_ids(product_ids: list[str]) -> list[str]:
    """Return any of these ids that are not in the catalogue."""
    if not product_ids:
        return []
    with _connect() as con:
        known = {
            row[0]
            for row in con.execute(
                f"SELECT product_id FROM catalogue WHERE product_id IN "
                f"({','.join('?' * len(product_ids))})",
                product_ids,
            )
        }
    return [p for p in product_ids if p not in known]
