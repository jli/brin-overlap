from datetime import datetime

from brin_lib import BlockRange, date_match, fully_within_dates, overlaps_dates

ts = datetime.fromtimestamp


def test_fully_within_dates():
    br = BlockRange(1, ts(10), ts(20))
    assert fully_within_dates(br, None, None)
    assert fully_within_dates(br, ts(9), None)
    assert fully_within_dates(br, None, ts(21))
    assert fully_within_dates(br, ts(9), ts(21))
    # excluded by single bound, only one value given
    assert not fully_within_dates(br, ts(11), None)
    assert not fully_within_dates(br, None, ts(19))
    # excluded by single bound, both values given
    assert not fully_within_dates(br, ts(1), ts(19))
    assert not fully_within_dates(br, ts(11), ts(100))
    # excluded by both bounds
    assert not fully_within_dates(br, ts(11), ts(19))


def test_fully_within_dates_edge():
    br = BlockRange(1, ts(10), ts(20))
    assert fully_within_dates(br, ts(10), None)
    assert fully_within_dates(br, None, ts(20))
    assert fully_within_dates(br, ts(10), ts(20))


# These test cases match test_fully_within_dates.
def test_overlaps_dates():
    br = BlockRange(1, ts(10), ts(20))
    # fully within, so naturally also overlaps.
    assert overlaps_dates(br, None, None)
    assert overlaps_dates(br, ts(9), None)
    assert overlaps_dates(br, None, ts(21))
    assert overlaps_dates(br, ts(9), ts(21))
    # not fully within, but overlapping
    assert overlaps_dates(br, ts(11), None)
    assert overlaps_dates(br, None, ts(19))
    assert overlaps_dates(br, ts(1), ts(19))
    assert overlaps_dates(br, ts(11), ts(100))
    assert overlaps_dates(br, ts(11), ts(19))
    # narrower range also overlaps
    assert overlaps_dates(br, ts(15), ts(17))


def test_overlaps_dates_fails():
    br = BlockRange(1, ts(10), ts(20))
    assert not overlaps_dates(br, ts(1), ts(5))
    assert not overlaps_dates(br, ts(50), ts(100))
    assert not overlaps_dates(br, None, ts(5))
    assert not overlaps_dates(br, ts(50), None)


def test_overlaps_dates_edge():
    br = BlockRange(1, ts(10), ts(20))
    # Same as test_fully_within_dates_edge cases.
    assert overlaps_dates(br, ts(10), None)
    assert overlaps_dates(br, None, ts(20))
    # Also match overlaps.
    assert overlaps_dates(br, None, ts(10))
    assert overlaps_dates(br, ts(20), None)


def test_date_match():
    br = BlockRange(1, ts(10), ts(20))
    assert date_match(br, "overlap", ts(5), ts(15))
    assert not date_match(br, "within", ts(5), ts(15))

    assert date_match(br, "overlap", ts(1), ts(100))
    assert date_match(br, "within", ts(1), ts(100))

    assert not date_match(br, "overlap", ts(100), ts(110))
    assert not date_match(br, "within", ts(100), ts(110))
