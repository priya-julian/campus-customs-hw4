"""Campus Customs backend.

For now this only reads the catalogue and serves product images, which is all the
storefront needs. The shopping agent grows into this same app later.
"""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

import agent as shop_agent
import auth
import tools as shop_tools
from models import ChatRequest, ChatResponse, ChatTurn, PageContext, ProductCard

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"
SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

app = FastAPI(title="Campus Customs API", version="0.1.0")

# The Vite dev server runs on its own origin, so the browser needs permission to call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# catalogue.image_file_path is relative to data/ ("products/foo.jpg"), so mounting data/
# itself lets us hand the front end "/media/" + that path unchanged.
if DATA_DIR.is_dir():
    app.mount("/media", StaticFiles(directory=DATA_DIR), name="media")


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise HTTPException(status_code=503, detail=f"Database not found at {DB_PATH}")
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def short_description(description: str, limit: int = 120) -> str:
    """First sentence of the description, trimmed to fit on a product card."""
    first = description.split(". ")[0].rstrip(".")
    if len(first) > limit:
        # Trimmed text ends in an ellipsis; a full stop on top of it reads as "…."
        return first[:limit].rsplit(" ", 1)[0] + "…"
    return first + "."


def product_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "product_id": row["product_id"],
        "name": row["name"],
        "garment_type": row["garment_type"],
        "description": row["description"],
        "short_description": short_description(row["description"]),
        # colors and search_tags are JSON-encoded TEXT in the database, not real columns.
        "colors": json.loads(row["colors"]),
        "search_tags": json.loads(row["search_tags"]),
        "price": row["price"],
        "image_url": f"/media/{row['image_file_path']}",
    }


@app.get("/api/health")
def health() -> dict[str, Any]:
    with connect() as con:
        count = con.execute("SELECT COUNT(*) FROM catalogue").fetchone()[0]
    return {"status": "ok", "products": count}


@app.get("/api/products")
def list_products() -> list[dict[str, Any]]:
    """The whole catalogue, each product carrying its availability.

    Stock comes back in one grouped query rather than one per product, so adding
    availability to the grid costs a single extra round trip to SQLite, not 102.
    """
    with connect() as con:
        rows = con.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        stock_rows = con.execute(
            "SELECT product_id, size, quantity FROM inventory"
        ).fetchall()

    by_product: dict[str, dict[str, int]] = {}
    for row in stock_rows:
        by_product.setdefault(row["product_id"], {})[row["size"]] = row["quantity"]

    products = []
    for row in rows:
        stock = by_product.get(row["product_id"], {})
        ordered = [s for s in SIZE_ORDER if s in stock]
        product = product_from_row(row)
        product["sizes_in_stock"] = [s for s in ordered if stock[s] > 0]
        product["sizes_sold_out"] = [s for s in ordered if stock[s] == 0]
        product["total_stock"] = sum(stock.values())
        products.append(product)
    return products


@app.get("/api/products/{product_id}")
def get_product(product_id: str) -> dict[str, Any]:
    with connect() as con:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"No product '{product_id}'")
        sizes = con.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    by_size = {s["size"]: s["quantity"] for s in sizes}
    product = product_from_row(row)
    product["sizes"] = [
        {"size": s, "quantity": by_size.get(s, 0), "in_stock": by_size.get(s, 0) > 0}
        for s in SIZE_ORDER
        if s in by_size
    ]
    product["total_stock"] = sum(by_size.values())
    return product


# --------------------------------------------------------------------------- accounts

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MIN_PASSWORD_LENGTH = 8


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("This field is required.")
        return value.strip()

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Enter a valid email address.")
        return value

    @field_validator("password")
    @classmethod
    def strong_enough(cls, value: str) -> str:
        if len(value) < MIN_PASSWORD_LENGTH:
            raise ValueError(f"Use at least {MIN_PASSWORD_LENGTH} characters.")
        return value


class LoginRequest(BaseModel):
    email: str
    password: str


def public_user(row: sqlite3.Row) -> dict[str, Any]:
    """The user fields the front end is allowed to see. Never includes the hash."""
    return {
        "id": row["id"],
        "name": row["name"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "email": row["email"],
    }


def current_user(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    """Resolve the signed-in user from an 'Authorization: Bearer <token>' header."""
    token = ""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()

    user_id = auth.read_token(token) if token else None
    if user_id is None:
        raise HTTPException(status_code=401, detail="Please sign in again.")

    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=401, detail="Please sign in again.")
    return public_user(row)


@app.post("/api/auth/signup", status_code=201)
def signup(body: SignupRequest) -> dict[str, Any]:
    full_name = f"{body.first_name} {body.last_name}"
    password_hash = auth.hash_password(body.password)

    with connect() as con:
        existing = con.execute(
            "SELECT 1 FROM users WHERE lower(email) = ?", (body.email,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="That email already has an account.")

        cursor = con.execute(
            """INSERT INTO users (name, first_name, last_name, email, password_hash)
               VALUES (?, ?, ?, ?, ?)""",
            (full_name, body.first_name, body.last_name, body.email, password_hash),
        )
        con.commit()
        row = con.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()

    return {"token": auth.create_token(row["id"]), "user": public_user(row)}


@app.post("/api/auth/login")
def login(body: LoginRequest) -> dict[str, Any]:
    email = body.email.strip().lower()
    with connect() as con:
        row = con.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()

    if row is None:
        # Spend the same time as a real check so a missing account is not detectable.
        auth.dummy_verify()
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")

    if not auth.verify_password(body.password, row["password_hash"]):
        # Deliberately the same message as above: do not reveal which half was wrong.
        raise HTTPException(status_code=401, detail="Email or password is incorrect.")

    return {"token": auth.create_token(row["id"]), "user": public_user(row)}


@app.get("/api/auth/me")
def me(user: dict[str, Any] = Depends(current_user)) -> dict[str, Any]:
    return user


# ------------------------------------------------------------------------------ chat

# How many past messages to replay to the agent for a signed-in shopper.
HISTORY_LIMIT = 12


def optional_user(authorization: str | None = Header(default=None)) -> dict[str, Any] | None:
    """Like current_user, but returns None instead of raising.

    The chat widget sits on every page, so a signed-out visitor can still use it — they
    just do not get their conversation saved.
    """
    try:
        return current_user(authorization)
    except HTTPException:
        return None


def load_history(con: sqlite3.Connection, user_id: int) -> list[ChatTurn]:
    rows = con.execute(
        """SELECT role, content FROM chat_messages
           WHERE user_id = ? ORDER BY id DESC LIMIT ?""",
        (user_id, HISTORY_LIMIT),
    ).fetchall()
    return [ChatTurn(role=r["role"], content=r["content"]) for r in reversed(rows)]


def cards_for(con: sqlite3.Connection, product_ids: list[str]) -> list[ProductCard]:
    """Turn the agent's product ids into cards built from catalogue rows.

    The model chooses *which* products to show; every number and image on the card comes
    from the database, so a hallucinated price cannot reach the screen. Unknown ids are
    dropped rather than rendered as an empty card.
    """
    cards: list[ProductCard] = []
    for product_id in product_ids[:6]:
        row = con.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            continue
        cards.append(
            ProductCard(
                product_id=row["product_id"],
                name=row["name"],
                price=row["price"],
                image_url=f"/media/{row['image_file_path']}",
                garment_type=row["garment_type"],
                short_description=short_description(row["description"]),
            )
        )
    return cards


def build_deps(
    con: sqlite3.Connection,
    user: dict[str, Any] | None,
    page: PageContext,
) -> shop_agent.ChatDeps:
    """Assemble what the agent is told about the shopper and the page they are on.

    Identity comes from the verified session, never from the request body, so a client
    cannot claim to be someone else. The page's product_id is checked against the
    catalogue before it is passed on — an unknown id is dropped rather than quoted back
    to the model as though it were real.
    """
    product_id = None
    product_name = None
    if page.product_id:
        row = con.execute(
            "SELECT product_id, name FROM catalogue WHERE product_id = ?", (page.product_id,)
        ).fetchone()
        if row is not None:
            product_id = row["product_id"]
            product_name = row["name"]

    return shop_agent.ChatDeps(
        shopper_name=user["name"] if user else None,
        shopper_email=user["email"] if user else None,
        page_path=page.path,
        product_id=product_id,
        product_name=product_name,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user: dict[str, Any] | None = Depends(optional_user),
) -> ChatResponse:
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Say something first.")
    if len(message) > 2000:
        raise HTTPException(status_code=422, detail="That message is too long.")

    with connect() as con:
        # A signed-in shopper's history comes from the database, not the browser, so it
        # survives a reload and cannot be rewritten by the client.
        history = load_history(con, user["id"]) if user else body.history
        deps = build_deps(con, user, body.page)

    try:
        answer = await shop_agent.answer(message, history, deps)
    except Exception as exc:  # noqa: BLE001 - surface a usable message, log the detail
        print(f"[chat] agent failed: {type(exc).__name__}: {exc}")
        raise HTTPException(
            status_code=502, detail="The assistant is unavailable right now."
        ) from exc

    # Honesty backstop: flag any dollar figure in the prose that matches no catalogue
    # price. Logged, never blocking — a price range or a total would trip it too.
    stray = shop_tools.unverified_prices(answer.reply)
    if stray:
        print(f"[chat] prices not found in catalogue: {', '.join(stray)}")

    with connect() as con:
        products = cards_for(con, answer.product_ids)

        saved = False
        if user:
            con.execute(
                "INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)",
                (user["id"], message),
            )
            con.execute(
                """INSERT INTO chat_messages (user_id, role, content, products_json)
                   VALUES (?, 'assistant', ?, ?)""",
                (
                    user["id"],
                    answer.reply,
                    json.dumps([p.model_dump() for p in products]) if products else None,
                ),
            )
            con.commit()
            saved = True

    return ChatResponse(reply=answer.reply, products=products, saved=saved)


@app.get("/api/chat/history")
def chat_history(user: dict[str, Any] = Depends(current_user)) -> list[dict[str, Any]]:
    """Past messages for the signed-in shopper, oldest first."""
    with connect() as con:
        rows = con.execute(
            """SELECT role, content, products_json FROM chat_messages
               WHERE user_id = ? ORDER BY id""",
            (user["id"],),
        ).fetchall()
    return [
        {
            "role": r["role"],
            "content": r["content"],
            "products": json.loads(r["products_json"]) if r["products_json"] else [],
        }
        for r in rows
    ]
