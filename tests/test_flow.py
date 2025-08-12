import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
os.environ.setdefault("OPENAI_API_KEY", "test")
from config import settings
from db.models import init_db
from db import repo
from core import flow


def setup_module(module):
    db_path = "botai.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    init_db()


def teardown_module(module):
    db_path = "botai.db"
    if os.path.exists(db_path):
        os.remove(db_path)


def test_new_user_prompt_verification():
    responses = flow.on_incoming_message("user1", "hola")
    assert responses == ["Ingresá el código de verificación enviado por email."]


def test_code_verifies_and_returns_credits():
    flow.on_incoming_message("user2", "hola")
    responses = flow.on_incoming_message("user2", "123456")
    assert responses[0] == "Verificación exitosa"
    assert responses[1] == f"Tenés {settings.CREDITS_DEFAULT} créditos."


def test_no_credits_shows_payment_link(monkeypatch):
    flow.on_incoming_message("user3", "hola")
    flow.on_incoming_message("user3", "123456")
    user = repo.get_or_create_user("user3")
    repo.update_credits(user.id, 0, "")

    called = False

    def fake_reply(user_id: int, text: str) -> str:
        nonlocal called
        called = True
        return "reply"

    monkeypatch.setattr(flow.ai, "generate_reply", fake_reply)
    responses = flow.on_incoming_message("user3", "que tal")
    assert responses == [f"Te quedaste sin créditos. Renová: {settings.PAYMENT_URL}"]
    assert called is False
