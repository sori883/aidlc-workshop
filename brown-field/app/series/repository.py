"""ReservationSeries の永続化アクセス。"""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import ReservationSeries


class SeriesRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, series: ReservationSeries) -> ReservationSeries:
        self.db.add(series)
        self.db.flush()
        return series

    def get(self, series_id: str) -> ReservationSeries | None:
        return self.db.get(ReservationSeries, series_id)
