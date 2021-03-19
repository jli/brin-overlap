from datetime import datetime

from brin_lib import BlockRange
from bro_relevant_blocks import block_range_matches

ts = datetime.fromtimestamp

def test_block_range_matches_point():
    br = BlockRange(1, ts(10), ts(20))
    assert block_range_matches(br, ts(15), None)
    assert block_range_matches(br, ts(10), None)
    assert block_range_matches(br, ts(20), None)
    assert not block_range_matches(br, ts(9), None)
    assert not block_range_matches(br, ts(21), None)

def test_block_range_matches_range():
    br = BlockRange(1, ts(10), ts(20))
    # contained within
    assert block_range_matches(br, ts(15), ts(18))
    # within, edge cases
    assert block_range_matches(br, ts(10), ts(11))
    assert block_range_matches(br, ts(19), ts(20))
    # overlaps
    assert block_range_matches(br, ts(8), ts(11))
    assert block_range_matches(br, ts(18), ts(21))
    # block contained by range
    assert block_range_matches(br, ts(5), ts(25))
