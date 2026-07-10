"""FastAPI アプリのエントリポイント。

- 起動時にテーブルを作成。
- 各 router を登録。
- ドメイン例外→HTTP ステータスのハンドラを登録。
"""
from __future__ import annotations

from fastapi import FastAPI

from app.availability.router import router as availability_router
from app.common.errors import register_exception_handlers
from app.db.database import create_all
from app.reservations.router import router as reservations_router
from app.rooms.router import router as rooms_router
from app.series.router import router as series_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="社内会議室予約システム",
        description="会議室の登録・予約・キャンセルとダブルブッキング防止を提供する REST API。",
        version="1.0.0",
    )

    register_exception_handlers(app)

    app.include_router(rooms_router)
    # 定期予約は単発予約より前に登録し、/reservations/recurring を優先的に解決する。
    app.include_router(series_router)
    app.include_router(reservations_router)
    app.include_router(availability_router)

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


# 起動時にテーブルを作成しておく（存在しなければ作成）。
create_all()
app = create_app()
