#%%
from __future__ import annotations

import csv
import re
from datetime import datetime
from typing import Iterable, Optional

from brin_lib import BlockRange


DT_TUPLE_REX = re.compile(
    r"\{"
    r"(?P<start>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)?(?:[\+-]\d{2})?"
    r" \.\. "
    r"(?P<end>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})(?:\.\d+)?(?:[\+-]\d{2})?"
    r"\}"
)


def parse_datetime_tuple(s: str) -> tuple[datetime, datetime]:
    if (match := DT_TUPLE_REX.search(s)) is not None:
        start, end = match.groups()
        return (datetime.fromisoformat(start), datetime.fromisoformat(end))
    else:
        raise RuntimeError(f"failed to parse datetime tuple: {s}")


def parse_csv_rows(
    csv_rows: Iterable[str],
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list[BlockRange]:
    reader = csv.reader(csv_rows)
    brs = []
    for i, row in enumerate(reader):
        if i == 0:
            assert row == ["blknum", "value"]
            continue
        blknum, value = row
        br = BlockRange(int(blknum), *parse_datetime_tuple(value))
        if within_dates(br, start, end):
            brs.append(br)
    # note: i expected this to be sorted already, but it's not! this makes the
    # viz look much nicer.
    brs = sorted(brs, key=lambda br: br.blknum)
    return brs


def parse_csv_file(
    filepath: str, start: Optional[datetime] = None, end: Optional[datetime] = None
) -> list[BlockRange]:
    with open(filepath) as f:
        return parse_csv_rows(f, start, end)


def within_dates(
    br: BlockRange, start: Optional[datetime], end: Optional[datetime]
) -> bool:
    """Test that the block range is contained within start and end."""
    return (start is None or start <= br.start) and (end is None or br.end <= end)


#%%
if __name__ == "__main__":
    blocks = parse_csv_file("brin_export_full.csv")
    for i, block in enumerate(blocks[:10]):
        print(f"{i:2d}   {block}")
