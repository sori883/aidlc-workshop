"""週次定期予約の出現日時生成（純粋関数）。

business-rules.md の BR-RS-G* / BR-RS-C6 に対応。
副作用なし・DB 非依存でテスト/PBT が容易。overlaps と同じ設計思想。
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

WEEK = timedelta(days=7)


def generate_occurrences(
    start_time: datetime,
    end_time: datetime,
    count: int | None,
    until: date | None,
    max_count: int = 52,
) -> list[tuple[datetime, datetime]]:
    """起点 (start_time, end_time) を1回目とし、7日刻みで各回の (start, end) を返す。

    - `count` 指定時: 合計 count 回。
    - `until` 指定時: 各回の「開始日」が until 以下（inclusive）の回まで。
    - `count` と `until` はちょうど一方のみ指定する（両方/両方未指定は ValueError）。
    - 生成数の上限は max_count。上限を超える場合でも呼び出し側が件数で検出できるよう、
      最大で max_count + 1 件まで生成して打ち切る（無制限生成を防ぐ）。
    """
    if (count is None) == (until is None):
        raise ValueError("count と until はちょうど一方のみ指定してください。")

    occurrences: list[tuple[datetime, datetime]] = []

    if count is not None:
        if count < 1:
            raise ValueError("count は 1 以上である必要があります。")
        for i in range(count):
            delta = WEEK * i
            occurrences.append((start_time + delta, end_time + delta))
            if len(occurrences) > max_count:
                break  # 上限超過。呼び出し側が件数で 400 判定する。
    else:
        # until は日付として扱い、開始日 <= until の回まで（inclusive）。
        assert until is not None
        i = 0
        while True:
            delta = WEEK * i
            occ_start = start_time + delta
            if occ_start.date() > until:
                break
            occurrences.append((occ_start, end_time + delta))
            if len(occurrences) > max_count:
                break  # 上限超過。呼び出し側が件数で 400 判定する。
            i += 1

    return occurrences
