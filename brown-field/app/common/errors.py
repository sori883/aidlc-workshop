"""ドメイン例外を HTTP レスポンスへマッピングする例外ハンドラ。"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.common.exceptions import ConflictError, NotFoundError, ValidationError


def register_exception_handlers(app: FastAPI) -> None:
    """アプリにドメイン例外→HTTP ステータスのハンドラを登録する。"""

    @app.exception_handler(ValidationError)
    async def _handle_validation(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(NotFoundError)
    async def _handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(ConflictError)
    async def _handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.message})
