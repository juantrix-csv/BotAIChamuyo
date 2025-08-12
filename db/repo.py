from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from .models import (
    Message,
    SessionLocal,
    User,
    Credit,
    Verification,
)


def get_session() -> Session:
    return SessionLocal()


def get_or_create_user(channel_id: str) -> User:
    with get_session() as session:
        user = session.query(User).filter_by(channel_id=channel_id).first()
        if user:
            return user
        user = User(channel_id=channel_id, state="unverified")
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_credits(user_id: int) -> Optional[Credit]:
    with get_session() as session:
        return session.query(Credit).filter_by(user_id=user_id).first()


def ensure_credits(user_id: int, initial: int) -> Credit:
    with get_session() as session:
        credit = session.query(Credit).filter_by(user_id=user_id).first()
        if credit is None:
            credit = Credit(
                user_id=user_id,
                initial_credits=initial,
                remaining=initial,
                milestones_alerted="",
            )
            session.add(credit)
            session.commit()
            session.refresh(credit)
        return credit


def update_credits(user_id: int, remaining: int, milestones_alerted: str) -> None:
    with get_session() as session:
        credit = session.query(Credit).filter_by(user_id=user_id).first()
        if credit is None:
            credit = Credit(
                user_id=user_id,
                initial_credits=remaining,
                remaining=remaining,
                milestones_alerted=milestones_alerted,
            )
            session.add(credit)
        else:
            credit.remaining = remaining
            credit.milestones_alerted = milestones_alerted
        session.commit()


def get_verification(user_id: int) -> Optional[Verification]:
    with get_session() as session:
        return session.query(Verification).filter_by(user_id=user_id).first()


def update_verification(
    user_id: int, attempts: int, blocked_until: Optional[datetime]
) -> Verification:
    with get_session() as session:
        ver = session.query(Verification).filter_by(user_id=user_id).first()
        if ver is None:
            ver = Verification(
                user_id=user_id, attempts=attempts, blocked_until=blocked_until
            )
            session.add(ver)
        else:
            ver.attempts = attempts
            ver.blocked_until = blocked_until
        session.commit()
        session.refresh(ver)
        return ver


def add_message(
    user_id: int, role: str, content: str, tokens: Optional[int], cost: int = 0
) -> Message:
    with get_session() as session:
        message = Message(
            user_id=user_id, role=role, content=content, tokens=tokens, cost=cost
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message
