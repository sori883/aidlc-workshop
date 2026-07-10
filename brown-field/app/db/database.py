"""SQLAlchemy のエンジン・セッション・宣言的ベースと DB セッション依存性を定義する。"""
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


def _engine_kwargs(url: str) -> dict:
    # SQLite はデフォルトで同一スレッドからの利用に制限されるため、
    # FastAPI（複数スレッド）で使えるよう check_same_thread を無効化する。
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(settings.database_url, **_engine_kwargs(settings.database_url))
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """全 ORM モデルの基底クラス。"""


def get_db() -> Iterator[Session]:
    """リクエストスコープの DB セッションを供給する FastAPI 依存性。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all() -> None:
    """未作成のテーブルを作成する（起動時に呼ぶ）。"""
    # models を import してマッパーを登録してから作成する。
    from app.db import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
