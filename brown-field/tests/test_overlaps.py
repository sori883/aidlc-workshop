"""overlaps 純粋関数の境界条件テスト（US-05 / BR-OV）。"""
from datetime import datetime

from app.availability.service import overlaps


def dt(h: int, m: int = 0) -> datetime:
    return datetime(2030, 1, 1, h, m)


def test_adjacent_is_not_overlap():
    # 10:00-11:00 と 11:00-12:00（隣接）は重ならない。
    assert overlaps(dt(10), dt(11), dt(11), dt(12)) is False
    assert overlaps(dt(11), dt(12), dt(10), dt(11)) is False


def test_exact_match_is_overlap():
    assert overlaps(dt(10), dt(11), dt(10), dt(11)) is True


def test_contained_is_overlap():
    # 10:30-10:45 は 10:00-11:00 に内包される。
    assert overlaps(dt(10), dt(11), dt(10, 30), dt(10, 45)) is True


def test_partial_overlap_back():
    # 10:30-11:30 は後方にはみ出す。
    assert overlaps(dt(10), dt(11), dt(10, 30), dt(11, 30)) is True


def test_partial_overlap_front():
    # 09:30-10:30 は前方にはみ出す。
    assert overlaps(dt(10), dt(11), dt(9, 30), dt(10, 30)) is True


def test_completely_before_is_not_overlap():
    assert overlaps(dt(10), dt(11), dt(8), dt(9)) is False


def test_completely_after_is_not_overlap():
    assert overlaps(dt(10), dt(11), dt(12), dt(13)) is False
