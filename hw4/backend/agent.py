"""The Campus Customs shop agent: entry point and wiring.

Builds a PydanticAI agent whose system prompt is prompts/prompt.md, gives it the catalogue
tools from tools.py, and makes it return the structured ShopAnswer from models.py.

Run a question straight through from the command line:

    python agent.py "what navy hoodies do you have?"
"""

from __future__ import annotations

import asyncio
import os
import secrets
import time
import sys  # noqa: E402
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.usage import UsageLimits

import audit
import tools
from models import ChatTurn, ProductDetail, ShopAnswer

HERE = Path(__file__).resolve().parent
PROMPT_PATH = HERE / "prompts" / "prompt.md"

# Everyday shopper questions. Cheap and fast, which matters for a chat widget.
MODEL = "gpt-5.6-luna"

# Reserved for the harder agent steps added later in the assignment. Chat does not need it
# yet, so nothing is paying for it today.
SMART_MODEL = "gpt-5.6-luna"

# One shopper turn should never need more than a few tool calls. This is the stop rule that
# keeps a confused loop from running up a bill.
USAGE_LIMITS = UsageLimits(request_limit=8)

# Shown when the provider's filter blocks a message outright. Stays in character and does
# not explain the filter, which would only invite probing.
FILTERED_REPLY = (
    "I can't help with that one. If there is something in the shop you are after — a price, "
    "a colour, whether your size is in — ask me that and I will look it up."
)

# How much of the conversation the agent sees. Enough for "do you have that in a medium?"
# to resolve, without resending an entire afternoon of chat on every turn.
HISTORY_TURNS = 12


@dataclass
class ChatDeps:
    """Everything the agent is told about *who* is asking and *where* they are asking it.

    PydanticAI passes this to every tool and to the dynamic instructions as
    `RunContext.deps`. It is assembled by the chat route from the authenticated session and
    the page context the widget reports — never from anything the model said, so the model
    cannot talk its way into a different shopper's identity.
    """

    shopper_name: str | None = None
    shopper_email: str | None = None
    page_path: str = "/"
    product_id: str | None = None
    product_name: str | None = None

    @property
    def is_signed_in(self) -> bool:
        return self.shopper_email is not None


def load_api_key() -> str:
    """Read PORTKEY_API_KEY from the environment, falling back to the project .env files.

    The key is never hard-coded and never logged.
    """
    # Walk up from backend/ looking for a .env, so the key can live beside the code or in
    # a shared project root above it. Nothing is overwritten once set.
    for folder in [HERE, *HERE.parents[:4]]:
        candidate = folder / ".env"
        if candidate.is_file():
            load_dotenv(candidate)
    key = os.getenv("PORTKEY_API_KEY")
    if not key:
        raise RuntimeError(
            "PORTKEY_API_KEY is not set. Put it in the AI Foundations .env file."
        )
    return key


def build_agent() -> Agent:
    """The shop agent, rebuilt whenever prompts/prompt.md changes.

    The cache is keyed on the prompt file's modification time. Without that key the agent
    is built once per process and an edit to prompt.md is invisible until a restart —
    uvicorn's reloader only watches .py files, so a prompt-only change does not trigger one.
    """
    return _build_agent(PROMPT_PATH.stat().st_mtime)


@lru_cache(maxsize=2)
def _build_agent(prompt_mtime: float) -> Agent:
    key = load_api_key()
    client = AsyncOpenAI(
        api_key=key,
        base_url=os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1"),
        default_headers={"x-portkey-api-key": key, "x-portkey-provider": "openai"},
    )
    model = OpenAIChatModel(MODEL, provider=OpenAIProvider(openai_client=client))

    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=ShopAnswer,
        system_prompt=PROMPT_PATH.read_text(),
        # One correction attempt per failed check, so a stuck model cannot loop.
        retries=2,
    )

    @agent.output_validator
    def only_real_products_and_prices(output: ShopAnswer) -> ShopAnswer:
        """Refuse a reply that names a product or a price the catalogue does not have.

        The prompt already forbids both. This is the part that enforces it: instead of
        logging the problem after the fact, the agent is handed the mistake and asked to
        fix it before the shopper ever sees the reply.
        """
        unknown = tools.unknown_product_ids(output.product_ids)
        if unknown:
            raise ModelRetry(
                f"These product_ids are not in the catalogue: {', '.join(unknown)}. "
                "Only return ids that a tool gave you in this conversation. "
                "Search again if you need to, then answer with real ids."
            )

        stray = tools.unverified_prices(output.reply)
        if stray:
            raise ModelRetry(
                f"Your reply contains {', '.join(stray)}, which does not match any price "
                "in the catalogue. Look the price up with a tool and quote it exactly. "
                "Do not add prices together or estimate a total."
            )

        return output

    @agent.instructions
    def shopper_and_page(ctx: RunContext[ChatDeps]) -> str:
        """Per-turn context appended to the system prompt.

        Kept out of prompt.md because it changes every request: who is signed in and what
        they are looking at. Guests get the guest line, not a blank.
        """
        deps = ctx.deps
        lines: list[str] = []

        if deps.is_signed_in:
            lines.append(
                f"You are talking to {deps.shopper_name} ({deps.shopper_email}), who is "
                "signed in. You may greet them by first name. Their conversation is saved, "
                "so you can refer back to it naturally."
            )
        else:
            lines.append(
                "You are talking to a guest who is not signed in. You do not know their "
                "name — do not ask for it, and do not guess. This conversation is not saved; "
                "if they ask about saving it, they can create an account."
            )

        if deps.product_name and deps.product_id:
            lines.append(
                f'The shopper is looking at the product page for "{deps.product_name}" '
                f"(product_id: {deps.product_id}). If they say \"this\", \"it\", or "
                "\"this one\" without naming a product, they almost certainly mean that "
                "item. Call get_page_product to read its details."
            )
        else:
            lines.append(f"The shopper is on the page {deps.page_path}.")

        return "\n\n".join(lines)

    # Registered with their docstrings, which is what the model reads to decide when to
    # call them. The bodies live in tools.py so they can be tested without a model.
    agent.tool_plain(tools.search_catalogue)
    agent.tool_plain(tools.get_product)
    agent.tool_plain(tools.check_stock)

    @agent.tool
    def get_page_product(ctx: RunContext[ChatDeps]) -> ProductDetail | None:
        """Look up the product whose page the shopper is currently on.

        Use this when the shopper refers to "this" or "it" without naming anything.
        Returns None when they are not on a product page — in that case ask which item
        they mean rather than guessing.
        """
        if not ctx.deps.product_id:
            return None
        return tools.get_product(ctx.deps.product_id)

    return agent

def _history_text(history: list[ChatTurn]) -> str:
    """Flatten recent turns into the prompt.

    The website is the source of truth for conversation history — it reloads from
    chat_messages — so each request is self-contained rather than relying on state held
    in this process.
    """
    recent = history[-HISTORY_TURNS:]
    if not recent:
        return ""
    lines = [("Shopper" if t.role == "user" else "You") + f": {t.content}" for t in recent]
    return "Earlier in this conversation:\n" + "\n".join(lines) + "\n\n"


async def answer(
    message: str,
    history: list[ChatTurn] | None = None,
    deps: ChatDeps | None = None,
) -> ShopAnswer:
    """Answer one shopper message, recording the whole loop in the audit trail."""
    agent = build_agent()
    deps = deps or ChatDeps()
    run_id = secrets.token_hex(4)
    started = time.monotonic()

    audit.append(
        "run_started",
        run_id,
        message=message,
        signed_in=deps.is_signed_in,
        page=deps.page_path,
        product_in_context=deps.product_id,
        model=MODEL,
        request_limit=USAGE_LIMITS.request_limit,
    )

    prompt = f"{_history_text(history or [])}Shopper: {message}"
    try:
        result = await agent.run(prompt, deps=deps, usage_limits=USAGE_LIMITS)
    except Exception as exc:
        blocked = _is_content_filtered(exc)
        audit.append(
            "run_stopped",
            run_id,
            stop_reason="blocked_by_provider_filter" if blocked else "error",
            error=f"{type(exc).__name__}: {exc}",
            seconds=round(time.monotonic() - started, 2),
        )
        if blocked:
            # The provider refused the prompt before the model saw it. That is a refusal,
            # not an outage, so answer like one instead of showing an error.
            return ShopAnswer(reply=FILTERED_REPLY, product_ids=[])
        raise

    _audit_loop(run_id, result)

    # `usage` is a property on this version of PydanticAI, not a method.
    usage = result.usage
    audit.append(
        "run_stopped",
        run_id,
        stop_reason="completed",
        products_returned=len(result.output.product_ids),
        model_requests=getattr(usage, "requests", None),
        seconds=round(time.monotonic() - started, 2),
    )
    return result.output


def _is_content_filtered(exc: Exception) -> bool:
    """Did the provider's own safety filter reject this, rather than something breaking?

    Comes back as a 400 from the upstream API, so it is indistinguishable from a bad
    request unless the body is inspected.
    """
    text = str(exc).lower()
    return "content_filter" in text or "response was filtered" in text


def _audit_loop(run_id: str, result: object) -> None:
    """Record one entry per tool call and per validator rejection.

    Walks the finished message history rather than wrapping each tool, so the trail
    reflects what the loop actually did. Only visible tool traffic is recorded — the
    model's private reasoning is never written to the file.
    """
    pending: dict[str, str] = {}
    for message in result.all_messages():  # type: ignore[attr-defined]
        for part in getattr(message, "parts", []):
            kind = type(part).__name__

            if kind == "ToolCallPart":
                pending[getattr(part, "tool_call_id", "") or part.tool_name] = part.tool_name
                if part.tool_name != "final_result":
                    audit.append("tool_call", run_id, tool=part.tool_name, args=part.args)

            elif kind == "ToolReturnPart" and part.tool_name != "final_result":
                audit.append(
                    "tool_result", run_id, tool=part.tool_name, result=_summarise(part.content)
                )

            elif kind == "RetryPromptPart":
                # The output validator rejected a reply and asked for a correction.
                audit.append(
                    "validator_retry",
                    run_id,
                    tool=getattr(part, "tool_name", None) or "output_validator",
                    reason=str(getattr(part, "content", "")),
                )


def _summarise(content: object) -> str:
    """One short line describing what a tool returned."""
    if content is None:
        return "None"
    for attr in ("total_matches", "total_in_filters"):
        if hasattr(content, attr):
            return (
                f"total_matches={content.total_matches} "
                f"total_in_filters={content.total_in_filters} showing={content.showing}"
            )
    if hasattr(content, "in_stock"):
        return f"found={content.found} quantity={content.quantity} in_stock={content.in_stock}"
    if hasattr(content, "product_id"):
        return f"{content.product_id} price={content.price} in_stock={content.sizes_in_stock}"
    return str(content)[:160]


def main() -> int:
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print(__doc__)
        return 1
    reply = asyncio.run(answer(question, deps=ChatDeps()))
    print(reply.reply)
    if reply.product_ids:
        print("\nproducts:", ", ".join(reply.product_ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
