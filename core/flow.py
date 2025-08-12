from __future__ import annotations

import re
from typing import List

from config import settings
from db import repo
from db.models import User
from . import credits, verification, ai

CODE_REGEX = re.compile(r"^\d{4,8}$")


def on_incoming_message(channel_id: str, text: str) -> List[str]:
    """Handle an incoming message and return bot responses."""
    user = repo.get_or_create_user(channel_id)
    repo.add_message(user.id, "user", text, tokens=None, cost=0)

    responses: List[str] = []

    if user.state in {"unverified", "verifying"}:
        if CODE_REGEX.fullmatch(text):
            result = verification.on_code_input(user.id, text)
            msg = result.get("message", "")
            responses.append(msg)
            repo.add_message(user.id, "assistant", msg, tokens=None, cost=0)
            if result.get("ok"):
                remaining = credits.get_remaining(user.id)
                credit_msg = f"Tenés {remaining} créditos."
                responses.append(credit_msg)
                repo.add_message(user.id, "assistant", credit_msg, tokens=None, cost=0)
        else:
            prompt = "Ingresá el código de verificación enviado por email."
            responses.append(prompt)
            repo.add_message(user.id, "assistant", prompt, tokens=None, cost=0)
            if user.state != "verifying":
                with repo.get_session() as session:
                    db_user = session.get(User, user.id)
                    if db_user:
                        db_user.state = "verifying"
                        session.commit()
        return responses

    # state == verified
    credit = credits.ensure_user_credits(user.id, settings.CREDITS_DEFAULT)
    if credit.remaining == 0:
        msg = f"Te quedaste sin créditos. Renová: {settings.PAYMENT_URL}"
        responses.append(msg)
        repo.add_message(user.id, "assistant", msg, tokens=None, cost=0)
        return responses

    ai_reply = ai.generate_reply(user.id, text)
    usage = credits.consume(user.id)
    remaining = usage["remaining"]
    for percent in usage["crossed_thresholds"]:
        alert = (
            f"Atención: te quedan <= {percent}% de tus créditos ({remaining} restantes)."
        )
        responses.append(alert)
        repo.add_message(user.id, "assistant", alert, tokens=None, cost=0)

    responses.append(ai_reply)
    repo.add_message(
        user.id,
        "assistant",
        ai_reply,
        tokens=None,
        cost=settings.CREDITS_COST_PER_MSG,
    )
    return responses
