#%%
from __future__ import annotations

import csv
import re
from datetime import datetime
from typing import Iterable, Literal, Optional

from brin_lib import BlockRange, date_match


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
    match_type: Literal["overlap", "within"] = "overlap",
) -> list[BlockRange]:
    reader = csv.reader(csv_rows)
    brs = []
    for i, row in enumerate(reader):
        if i == 0:
            assert row == ["blknum", "value"]
            continue
        blknum, value = row
        br = BlockRange(int(blknum), *parse_datetime_tuple(value))
        if date_match(br, match_type, start, end):
            brs.append(br)
    # note: not sorted because bug in export_brin_items.sh sorting different
    # files. sorting makes viz look much nicer.
    brs = sorted(brs, key=lambda br: br.blknum)
    return brs


def parse_csv_file(
    filepath: str,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    match_type: Literal["overlap", "within"] = "overlap",
) -> list[BlockRange]:
    with open(filepath) as f:
        return parse_csv_rows(f, start, end, match_type)


#%%
if __name__ == "__main__":
    blocks = parse_csv_file("brin_export_full.csv")
    for i, block in enumerate(blocks[:10]):
        print(f"{i:2d}   {block}")
