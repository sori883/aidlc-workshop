"""アプリケーション設定。

環境変数で上書き可能。テスト時は DATABASE_URL を差し替える。
"""
import os


class Settings:
    """実行時設定を環境変数から読み込む。"""

    def __init__(self) -> None:
        self.database_url: str = os.getenv("DATABASE_URL", "sqlite:///./reservations.db")
        self.host: str = os.getenv("HOST", "127.0.0.1")
        self.port: int = int(os.getenv("PORT", "8000"))


settings = Settings()
