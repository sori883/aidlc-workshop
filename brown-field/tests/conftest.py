"""テスト共通フィクスチャ。

本番DBと分離するため、テスト用の一時 SQLite（ファイル）を使い、
アプリの get_db 依存性を差し替える。
"""
from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def client() -> Iterator[TestClient]:
    # 一時ファイルの SQLite を用意（テストごとに分離）。
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    test_url = f"sqlite:///{path}"

    # database モジュールのエンジン/セッションをテスト用に差し替える。
    from app.db import database

    engine = create_engine(test_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    database.engine = engine
    database.SessionLocal = TestingSessionLocal
    database.Base.metadata.create_all(bind=engine)

    from app.main import create_app

    app = create_app()

    def override_get_db() -> Iterator:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    engine.dispose()
    os.unlink(path)


def create_room(client: TestClient, name: str = "Room A", capacity: int = 4) -> str:
    """テスト用ヘルパー: 会議室を作成して ID を返す。"""
    resp = client.post(
        "/rooms",
        json={
            "name": name,
            "capacity": capacity,
            "equipment": ["projector"],
            "location": "3F",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]
