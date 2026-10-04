"""Shared Pydantic types for the Campus Customs shop agent.

Two things live here: the structured answer the agent is required to produce, and the
shapes the website exchanges with FastAPI. Keeping them in one file means the chat route,
the agent, and the tools all agree on what a product looks like.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

SIZES = ["XS", "S", "M", "L", "XL", "XXL"]


# ----------------------------------------------------------------- what tools hand back

class SizeStock(BaseModel):
    """Stock for one size of one product."""

    size: str
    quantity: int
    in_stock: bool


class ProductSummary(BaseModel):
    """A catalogue row as the agent sees it while searching.

    Carries availability as well as the description, so the agent can avoid recommending
    something that is sold out everywhere without spending a tool call per candidate.
    """

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    sizes_in_stock: list[str] = Field(
        default_factory=list, description="Sizes with at least one unit on the shelf."
    )
    sizes_sold_out: list[str] = Field(
        default_factory=list, description="Sizes currently at zero."
    )
    total_stock: int = Field(default=0, description="Units on hand across every size.")


class ProductDetail(ProductSummary):
    """One product with its stock broken out size by size.

    Adds the per-size counts on top of the summary's roll-up, for when a shopper asks how
    many are left rather than merely whether their size exists.
    """

    sizes: list[SizeStock]


class SearchResults(BaseModel):
    """What a catalogue search returns.

    `total_matches` is the whole story; `products` is the capped slice. Without the count
    the agent cannot tell "these are the six that matched" from "these are six of 25", and
    it was reporting the second as though it were the first.
    """

    total_matches: int = Field(
        description=(
            "How many products matched your search words AND the filters. This is NOT the "
            "number of items in the price range — narrow search words make it smaller."
        )
    )
    total_in_filters: int = Field(
        description=(
            "How many products satisfy the price/stock filters alone, ignoring your search "
            "words. Quote this one when the shopper asked purely about budget or stock, "
            "e.g. 'what do you have under $40'."
        )
    )
    showing: int = Field(description="How many products are in this list.")
    products: list[ProductSummary] = Field(default_factory=list)
    filters_applied: str | None = Field(
        default=None, description="Human-readable note of any price or stock filter used."
    )


class StockAnswer(BaseModel):
    """The answer to "do you have this in a <size>?".

    `found` separates "we checked and there are none" from "that is not a thing we stock",
    which are different sentences to say to a shopper.
    """

    product_id: str
    product_name: str | None = None
    size: str
    found: bool = Field(description="False when the product or that size does not exist.")
    quantity: int = Field(default=0, description="Units on hand. Meaningful only when found.")
    in_stock: bool = Field(default=False, description="True when quantity is above zero.")
    reason: str | None = Field(
        default=None, description="Why the lookup failed, when found is False."
    )
    sizes_in_stock: list[str] = Field(
        default_factory=list,
        description="Other sizes of this product that are available, to offer as alternatives.",
    )


# ------------------------------------------------------------- what the agent must return

class ShopAnswer(BaseModel):
    """The agent's structured reply.

    `product_ids` is deliberately only a list of ids, not full product objects. The server
    looks each id up in the catalogue and builds the card from the database row, so a price
    or an image on screen can never be something the model made up.
    """

    reply: str = Field(
        description=(
            "The message to show the shopper. Markdown is fine. Keep it short and plain, "
            "and never state a price or stock figure that did not come from a tool."
        )
    )
    product_ids: list[str] = Field(
        default_factory=list,
        description=(
            "product_id values for the items this reply is about, so the site can show them "
            "as cards. Leave empty when the reply is not about specific products. Order "
            "matters: most relevant first. At most 6."
        ),
    )


# --------------------------------------------------------------- what the website exchanges

class ProductCard(BaseModel):
    """A product as rendered in the chat panel. Every field comes from the database."""

    product_id: str
    name: str
    price: float
    image_url: str
    garment_type: str
    short_description: str


class ChatTurn(BaseModel):
    """One message in a conversation."""

    role: str  # "user" or "assistant"
    content: str


class PageContext(BaseModel):
    """Where the shopper is standing when they ask.

    Sent by the chat widget with every message. It is what lets "do you have this in pink?"
    resolve to an actual garment: the widget reports the route, the server turns a product
    route into a real catalogue row, and the agent is told which item "this" means.
    """

    path: str = Field(default="/", description="The route the shopper is on, e.g. /products/x.")
    product_id: str | None = Field(
        default=None, description="Set when the shopper is on a single-product page."
    )


class ChatRequest(BaseModel):
    message: str
    page: PageContext = Field(default_factory=PageContext)
    # Used only for signed-out shoppers. When a request is authenticated the server reads
    # history from chat_messages instead and ignores whatever the client sent.
    history: list[ChatTurn] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    products: list[ProductCard] = Field(default_factory=list)
    saved: bool = Field(
        default=False,
        description="True when this exchange was written to chat_messages for a signed-in user.",
    )
