"""User verification workflow."""

from __future__ import annotations

import logging
import math
from datetime import datetime, timedelta, timezone
from typing import Tuple

from config import settings
from db import repo
from db.models import User

logger = logging.getLogger(__name__)


BLOCK_ATTEMPTS = 5
BLOCK_MINUTES = 15


def _mask_code(code: str) -> str:
    """Return the code masked except for the last two digits."""
    suffix = code[-2:] if len(code) >= 2 else code
    return f"***{suffix}"


def is_blocked(user_id: int) -> Tuple[bool, int]:
    """Return whether the user is blocked and remaining seconds."""
    ver = repo.get_verification(user_id)
    if ver and ver.blocked_until:
        now = datetime.now(timezone.utc)
        if ver.blocked_until > now:
            remaining = int((ver.blocked_until - now).total_seconds())
            return True, remaining
    return False, 0


def verify_code(user_id: int, code: str) -> bool:
    """Stub verification: returns True if the code matches."""
    logger.info("Verifying code for user %s: %s", user_id, _mask_code(code))
    return code == "123456"


def on_code_input(user_id: int, code: str) -> dict:
    """Process a verification code input for a user."""
    blocked, remaining = is_blocked(user_id)
    if blocked:
        minutes = max(1, math.ceil(remaining / 60))
        return {"ok": False, "message": f"Bloqueado {minutes} min"}

    if verify_code(user_id, code):
        repo.update_verification(user_id, 0, None)
        with repo.get_session() as session:
            user = session.get(User, user_id)
            if user:
                user.state = "verified"
                session.commit()
        repo.ensure_credits(user_id, settings.CREDITS_DEFAULT)
        return {"ok": True, "message": "Verificación exitosa"}

    ver = repo.get_verification(user_id)
    attempts = ver.attempts + 1 if ver else 1
    blocked_until = None
    if attempts >= BLOCK_ATTEMPTS:
        blocked_until = datetime.now(timezone.utc) + timedelta(minutes=BLOCK_MINUTES)
        attempts = 0
    repo.update_verification(user_id, attempts, blocked_until)
    return {"ok": False, "message": "Código incorrecto. Intentá de nuevo"}
