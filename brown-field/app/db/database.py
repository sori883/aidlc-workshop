"""SQLAlchemy のエンジン・セッション・宣言的ベースと DB セッション依存性を定義する。"""
from collections.abc import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
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


def _ensure_series_id_column(bind: Engine) -> None:
    """既存の reservations テーブルに series_id 列が無ければ追加する（冪等）。

    Base.metadata.create_all は未作成テーブルしか作らず、既存テーブルへの列追加は
    行わないため、定期予約機能で追加した series_id を既存 DB にも反映する。
    """
    inspector = inspect(bind)
    # reservations テーブルが未作成なら create_all 側で新スキーマとして作られるため何もしない。
    if "reservations" not in inspector.get_table_names():
        return
    columns = {col["name"] for col in inspector.get_columns("reservations")}
    if "series_id" not in columns:
        with bind.begin() as conn:
            conn.execute(
                text("ALTER TABLE reservations ADD COLUMN series_id VARCHAR(36)")
            )


def create_all() -> None:
    """未作成のテーブルを作成し、既存テーブルへ不足列を補う（起動時に呼ぶ）。"""
    # models を import してマッパーを登録してから作成する。
    from app.db import models  # noqa: F401

    # 既存 reservations への列追加は create_all より前に行う
    # （新規 DB の場合はテーブル未作成なのでスキップされ、create_all が新スキーマで作成）。
    _ensure_series_id_column(engine)
    Base.metadata.create_all(bind=engine)
