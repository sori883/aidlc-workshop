"""Property-Based Tests（Hypothesis）— recurring-reservations。

PBT Partial モードで強制対象の PBT-02（Round-trip）/ PBT-03（Invariant）/
PBT-07（Generator quality）/ PBT-08（shrinking・seed 再現性は Hypothesis 既定）に対応。
純粋関数・スキーマが対象のため DB 非依存。
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

from hypothesis import given
from hypothesis import strategies as st

from app.series.recurrence import generate_occurrences
from app.series.schemas import RecurringReservationCreate

# --- PBT-07: ドメイン生成器 -------------------------------------------------

# 現実的な範囲の起点日時（秒・マイクロ秒は0に丸め、時刻は業務時間帯）。
base_datetimes = st.datetimes(
    min_value=datetime(2030, 1, 1, 0, 0),
    max_value=datetime(2035, 12, 31, 0, 0),
).map(lambda d: d.replace(minute=0, second=0, microsecond=0))

durations = st.integers(min_value=1, max_value=8).map(lambda h: timedelta(hours=h))
counts = st.integers(min_value=1, max_value=52)


# --- PBT-03: Invariant（generate_occurrences） ------------------------------


@given(start=base_datetimes, dur=durations, count=counts)
def test_count_invariant_length(start, dur, count):
    occ = generate_occurrences(start, start + dur, count=count, until=None)
    # 生成数は count と一致（count <= 52）。
    assert len(occ) == count


@given(start=base_datetimes, dur=durations, count=counts)
def test_count_invariant_weekly_step_and_weekday(start, dur, count):
    occ = generate_occurrences(start, start + dur, count=count, until=None)
    # 各回は7日間隔で、開始時刻・曜日・継続時間が保存される。
    for i, (s, e) in enumerate(occ):
        assert s == start + timedelta(days=7 * i)
        assert e - s == dur
        assert s.weekday() == start.weekday()
        assert s.hour == start.hour


@given(start=base_datetimes, dur=durations, weeks=st.integers(min_value=0, max_value=60))
def test_until_invariant_boundary(start, dur, weeks):
    until = (start + timedelta(weeks=weeks)).date()
    occ = generate_occurrences(start, start + dur, count=None, until=until, max_count=52)
    if not occ:
        return
    # 全回の開始日は until 以下（inclusive）。
    for s, _ in occ:
        assert s.date() <= until
    # 上限内なら、次の回は until を超える（境界の正しさ）。
    if len(occ) <= 52:
        nxt = occ[-1][0] + timedelta(days=7)
        assert nxt.date() > until or len(occ) > 52


# --- PBT-02: Round-trip（スキーマのシリアライズ往復） ------------------------


@given(
    room_id=st.uuids().map(str),
    start=base_datetimes,
    dur=durations,
    name=st.text(min_size=1, max_size=20).filter(lambda s: s.strip() != ""),
    count=counts,
)
def test_recurring_create_roundtrip(room_id, start, dur, name, count):
    original = RecurringReservationCreate(
        room_id=room_id,
        start_time=start,
        end_time=start + dur,
        booker_name=name,
        count=count,
        until=None,
    )
    # model_dump -> model_validate の往復で同値。
    restored = RecurringReservationCreate.model_validate(original.model_dump())
    assert restored == original


@given(
    room_id=st.uuids().map(str),
    start=base_datetimes,
    dur=durations,
    name=st.text(min_size=1, max_size=20).filter(lambda s: s.strip() != ""),
    weeks=st.integers(min_value=0, max_value=52),
)
def test_recurring_create_until_roundtrip(room_id, start, dur, name, weeks):
    until = (start + timedelta(weeks=weeks)).date()
    original = RecurringReservationCreate(
        room_id=room_id,
        start_time=start,
        end_time=start + dur,
        booker_name=name,
        count=None,
        until=until,
    )
    restored = RecurringReservationCreate.model_validate(original.model_dump())
    assert restored == original
    assert isinstance(restored.until, date)
