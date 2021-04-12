from __future__ import annotations

from datetime import datetime

from brin_lib import BlockRange
from brin_overlap import compute_overlap, find_position, try_insert


def blknums(brs: list[BlockRange]) -> list[int]:
    return [br.blknum for br in brs]


def test_find_position() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    c = BlockRange(3, datetime.fromtimestamp(5), datetime.fromtimestamp(6))
    assert find_position([b, c], a) == 0
    assert find_position([a, c], b) == 1
    assert find_position([a, b], c) == 2


def test_find_position_equal_endpoints() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(2), datetime.fromtimestamp(3))
    c = BlockRange(3, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    assert find_position([b, c], a) == 0
    assert find_position([a, c], b) == 1
    assert find_position([a, b], c) == 2


def test_find_position_overlap() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    ab = BlockRange(3, datetime.fromtimestamp(2), datetime.fromtimestamp(4))
    assert find_position([a, b], ab) is None
    assert find_position([a, ab], b) is None


def test_try_insert() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    c = BlockRange(3, datetime.fromtimestamp(5), datetime.fromtimestamp(6))
    level = [a, c]
    assert try_insert(level, b)
    assert blknums(level) == [1, 2, 3]
    level = [a, b]
    assert try_insert(level, c)
    assert blknums(level) == [1, 2, 3]
    level = [b, c]
    assert try_insert(level, a)
    assert blknums(level) == [1, 2, 3]


def test_try_insert_fail() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    ab1 = BlockRange(3, datetime.fromtimestamp(1), datetime.fromtimestamp(4))
    ab2 = BlockRange(3, datetime.fromtimestamp(1), datetime.fromtimestamp(3))
    ab3 = BlockRange(3, datetime.fromtimestamp(2), datetime.fromtimestamp(4))
    levels = [a, b]
    assert not try_insert(levels, ab1)
    assert not try_insert(levels, ab2)
    assert not try_insert(levels, ab3)


def test_try_insert_edge() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    # empty list
    level: list[BlockRange] = []
    assert try_insert(level, a)
    assert blknums(level) == [1]
    # insert before first element
    level = [b]
    assert try_insert(level, a)
    assert blknums(level) == [1, 2]
    # insert after last element
    level = [a]
    assert try_insert(level, b)
    assert blknums(level) == [1, 2]


def test_compute_overlap_ordered() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    c = BlockRange(3, datetime.fromtimestamp(5), datetime.fromtimestamp(6))
    d = BlockRange(4, datetime.fromtimestamp(7), datetime.fromtimestamp(8))
    bro = compute_overlap([a, b, c, d])
    assert bro.min_val.timestamp() == 1
    assert bro.max_val.timestamp() == 8
    assert bro.min_blknum == 1
    assert bro.max_blknum == 4
    assert len(bro.levels) == 1
    assert blknums(bro.levels[0]) == [1, 2, 3, 4]


def test_compute_overlap_overlap() -> None:
    a = BlockRange(1, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    b = BlockRange(2, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    c = BlockRange(3, datetime.fromtimestamp(3), datetime.fromtimestamp(4))
    d = BlockRange(4, datetime.fromtimestamp(1), datetime.fromtimestamp(2))
    bro = compute_overlap([a, b, c, d])
    assert bro.min_val.timestamp() == 1
    assert bro.max_val.timestamp() == 4
    assert bro.min_blknum == 1
    assert bro.max_blknum == 4
    assert len(bro.levels) == 2
    assert blknums(bro.levels[0]) == [1, 2]
    assert blknums(bro.levels[1]) == [4, 3]
