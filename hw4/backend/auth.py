"""Password hashing and session tokens for Campus Customs.

Passwords are never stored or logged in plaintext. What goes in the database is a salted
PBKDF2-HMAC-SHA256 digest, which is slow to compute by design: an attacker holding a stolen
copy of the table still has to spend ~600k hash rounds per password per guess, and the
per-user salt means they cannot attack every row at once with one rainbow table.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from pathlib import Path

ALGORITHM = "pbkdf2_sha256"

# OWASP's current floor for PBKDF2-HMAC-SHA256. Used for every password set from now on.
ITERATIONS = 600_000

# The seeded accounts were hashed before this app existed, in a 3-part format with no
# iteration count recorded. That shape implies the original work factor, so we can still
# verify those users instead of locking them out.
LEGACY_ITERATIONS = 120_000

SALT_BYTES = 16
TOKEN_TTL_SECONDS = 14 * 24 * 60 * 60  # 14 days


# --------------------------------------------------------------------------- passwords

def hash_password(password: str, *, iterations: int = ITERATIONS) -> str:
    """Return 'pbkdf2_sha256$<iterations>$<salt>$<hex digest>'."""
    salt = secrets.token_hex(SALT_BYTES)
    digest = _pbkdf2(password, salt, iterations)
    return f"{ALGORITHM}${iterations}${salt}${digest}"


def verify_password(password: str, stored: str) -> bool:
    """Check a password against either the current or the seeded hash format."""
    try:
        parts = stored.split("$")
        if len(parts) == 4:
            algorithm, iterations_text, salt, expected = parts
            iterations = int(iterations_text)
        elif len(parts) == 3:
            algorithm, salt, expected = parts
            iterations = LEGACY_ITERATIONS
        else:
            return False
        if algorithm != ALGORITHM:
            return False
    except (ValueError, AttributeError):
        return False

    # compare_digest, not ==, so the comparison does not leak how much of the digest
    # matched through how long it took to fail.
    return hmac.compare_digest(_pbkdf2(password, salt, iterations), expected)


def dummy_verify() -> None:
    """Burn a comparable amount of time when an email is not found.

    Without this, a missing account answers noticeably faster than a wrong password, which
    tells an attacker which email addresses are registered.
    """
    _pbkdf2("not-a-real-password", "not-a-real-salt", ITERATIONS)


def _pbkdf2(password: str, salt: str, iterations: int) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    ).hex()


# ----------------------------------------------------------------------------- sessions

def _load_secret() -> bytes:
    """Signing key for session tokens.

    Prefers SESSION_SECRET from the environment. Falls back to a random key cached in a
    gitignored file so that logins survive a dev-server reload without a secret ever being
    written into source.
    """
    from_env = os.environ.get("SESSION_SECRET")
    if from_env:
        return from_env.encode("utf-8")

    cache = Path(__file__).resolve().parent / ".session_secret"
    if not cache.exists():
        cache.write_text(secrets.token_hex(32))
        cache.chmod(0o600)
    return cache.read_text().strip().encode("utf-8")


_SECRET = _load_secret()


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def create_token(user_id: int) -> str:
    """Signed '<payload>.<signature>' token naming the user and when it expires."""
    payload = _b64(json.dumps({"uid": user_id, "exp": int(time.time()) + TOKEN_TTL_SECONDS}).encode())
    signature = _b64(hmac.new(_SECRET, payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"


def read_token(token: str) -> int | None:
    """Return the user id if the token is intact and unexpired, else None."""
    try:
        payload, signature = token.split(".")
    except (ValueError, AttributeError):
        return None

    expected = _b64(hmac.new(_SECRET, payload.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(signature, expected):
        return None

    try:
        data = json.loads(_unb64(payload))
    except (ValueError, json.JSONDecodeError):
        return None

    if data.get("exp", 0) < time.time():
        return None
    return data.get("uid")
