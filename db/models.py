from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.sql import func

DATABASE_URL = "sqlite:///./botai.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, unique=True, nullable=False)
    state = Column(String, nullable=False, default="unverified")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    credits = relationship("Credit", back_populates="user", uselist=False)
    verification = relationship("Verification", back_populates="user", uselist=False)
    messages = relationship("Message", back_populates="user")


class Credit(Base):
    __tablename__ = "credits"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    initial_credits = Column(Integer, nullable=False)
    remaining = Column(Integer, nullable=False)
    milestones_alerted = Column(Text)
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="credits")


class Verification(Base):
    __tablename__ = "verifications"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    attempts = Column(Integer, nullable=False, default=0)
    blocked_until = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="verification")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    tokens = Column(Integer)
    cost = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="messages")


def init_db() -> None:
    """Create database tables."""
    Base.metadata.create_all(bind=engine)
