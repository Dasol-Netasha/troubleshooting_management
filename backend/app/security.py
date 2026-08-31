from __future__ import annotations

import hashlib
import hmac
import os
from base64 import urlsafe_b64decode, urlsafe_b64encode

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 120_000


def _b64_encode(raw: bytes) -> str:
    return urlsafe_b64encode(raw).decode("ascii")


def _b64_decode(encoded: str) -> bytes:
    return urlsafe_b64decode(encoded.encode("ascii"))


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${_b64_encode(salt)}${_b64_encode(digest)}"


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iteration_text, encoded_salt, encoded_digest = encoded_hash.split("$", 3)
        if algorithm != ALGORITHM:
            return False

        iterations = int(iteration_text)
        salt = _b64_decode(encoded_salt)
        expected_digest = _b64_decode(encoded_digest)
        actual_digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual_digest, expected_digest)
    except Exception:
        return False