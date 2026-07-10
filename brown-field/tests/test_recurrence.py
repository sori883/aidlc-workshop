"""generate_occurrences 純粋関数の境界条件テスト（US-R01/US-R03 / BR-RS-G*）。"""
from datetime import date, datetime

import pytest

from app.series.recurrence import generate_occurrences


def dt(day: int, h: int = 10) -> datetime:
    # 2030-01-07 は月曜。曜日固定の確認に使う。
    return datetime(2030, 1, day, h, 0)


def test_count_generates_exact_number():
    occ = generate_occurrences(dt(7), dt(7, 11), count=4, until=None)
    assert len(occ) == 4


def test_count_is_weekly_7_day_step():
    occ = generate_occurrences(dt(7), dt(7, 11), count=3, until=None)
    starts = [s for s, _ in occ]
    assert starts[0] == datetime(2030, 1, 7, 10)
    assert starts[1] == datetime(2030, 1, 14, 10)
    assert starts[2] == datetime(2030, 1, 21, 10)


def test_count_preserves_time_of_day_and_weekday():
    occ = generate_occurrences(dt(7), dt(7, 11), count=3, until=None)
    for s, e in occ:
        assert s.hour == 10 and e.hour == 11
        assert s.weekday() == 0  # 月曜固定


def test_until_inclusive_boundary():
    # 起点 1/7、until 1/21 -> 1/7, 1/14, 1/21 の3回（inclusive）。
    occ = generate_occurrences(dt(7), dt(7, 11), count=None, until=date(2030, 1, 21))
    starts = [s.date() for s, _ in occ]
    assert starts == [date(2030, 1, 7), date(2030, 1, 14), date(2030, 1, 21)]


def test_until_excludes_after_boundary():
    # until 1/20 -> 1/21 は含まない -> 1/7, 1/14 の2回。
    occ = generate_occurrences(dt(7), dt(7, 11), count=None, until=date(2030, 1, 20))
    assert len(occ) == 2


def test_until_before_start_yields_empty():
    occ = generate_occurrences(dt(7), dt(7, 11), count=None, until=date(2030, 1, 1))
    assert occ == []


def test_over_max_count_is_bounded():
    # count=100 は上限52を超えるため、max_count+1 で打ち切られる（呼び出し側が400判定）。
    occ = generate_occurrences(dt(7), dt(7, 11), count=100, until=None, max_count=52)
    assert len(occ) == 53


def test_requires_exactly_one_end_condition():
    with pytest.raises(ValueError):
        generate_occurrences(dt(7), dt(7, 11), count=None, until=None)
    with pytest.raises(ValueError):
        generate_occurrences(dt(7), dt(7, 11), count=3, until=date(2030, 1, 21))


def test_count_must_be_positive():
    with pytest.raises(ValueError):
        generate_occurrences(dt(7), dt(7, 11), count=0, until=None)
