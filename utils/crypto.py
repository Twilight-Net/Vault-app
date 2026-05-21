"""
utils/crypto.py — Encryption and decryption helpers using Fernet (AES-128-CBC + HMAC-SHA256).

A single app-level key is loaded from the environment (VAULT_FERNET_KEY).
On first run, a key is auto-generated and written to .vault_key for convenience.
In production, store the key in a real secret manager or environment variable.
"""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet


_KEY_FILE = Path(__file__).parent.parent / ".vault_key"


def _load_or_create_key() -> bytes:
    """Load the Fernet key from env → .vault_key file → generate new one."""
    env_key = os.environ.get("VAULT_FERNET_KEY")
    if env_key:
        return env_key.encode()

    if _KEY_FILE.exists():
        return _KEY_FILE.read_bytes().strip()

    # First-run: generate and persist
    key = Fernet.generate_key()
    _KEY_FILE.write_bytes(key)
    print(f"[VAULT] Generated new encryption key → {_KEY_FILE}")
    return key


_FERNET = Fernet(_load_or_create_key())


def encrypt(plaintext: str) -> str:
    """Encrypt a UTF-8 string and return a URL-safe base64 token string."""
    if not plaintext:
        return ""
    token = _FERNET.encrypt(plaintext.encode("utf-8"))
    return token.decode("utf-8")


def decrypt(token: str) -> str:
    """Decrypt a Fernet token string and return the original plaintext."""
    if not token:
        return ""
    try:
        plaintext = _FERNET.decrypt(token.encode("utf-8"))
        return plaintext.decode("utf-8")
    except Exception:
        # Return placeholder on tampered / invalid token
        return "[decryption error]"
