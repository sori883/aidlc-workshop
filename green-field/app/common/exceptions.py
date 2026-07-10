"""ドメイン例外。router 層で HTTP ステータスにマッピングされる。"""


class DomainError(Exception):
    """ドメイン例外の基底。"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(DomainError):
    """参照先が存在しない（-> 404）。"""


class ConflictError(DomainError):
    """重複予約・active 予約ありの会議室削除など（-> 409）。"""


class ValidationError(DomainError):
    """業務的な入力検証違反（-> 400）。"""
