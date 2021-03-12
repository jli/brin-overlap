#%%
from __future__ import annotations

import csv
import re
from dataclasses_json import dataclass_json
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


# TODO: handle non-datetime values
@dataclass_json
@dataclass
class BlockRange:
    blknum: int
    start: datetime
    end: datetime

    def __repr__(self):
        def t(dt):
            return dt.strftime("%Y%m%d %H:%M:%S")

        return f"BR({self.blknum}, {t(self.start)}..{t(self.end)})"


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


def parse_csv_rows(csv_rows: Iterable[str]) -> list[BlockRange]:
    reader = csv.reader(csv_rows)
    brs = []
    for i, row in enumerate(reader):
        if i == 0:
            assert row == ["blknum", "value"]
            continue
        blknum, value = row
        brs.append(BlockRange(int(blknum), *parse_datetime_tuple(value)))
    return brs


def parse_csv_file(filepath: str) -> list[BlockRange]:
    with open(filepath) as f:
        return parse_csv_rows(f)

#%%
if __name__ == "__main__":
    with open("brin_export_full.csv") as f:
        blocks = parse_csv_rows(f)
    for i, block in enumerate(blocks[:10]):
        print(f"{i:2d}   {block}")
