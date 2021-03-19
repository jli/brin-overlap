#!/usr/bin/env python3

"""Query CSV for relevant blocks."""

#%%
import argparse
import math
from datetime import datetime
from typing import Optional

from brin_lib import BlockRange
from brin_parser import parse_csv_file


def block_range_contains(br: BlockRange, dt: datetime, dt_end: Optional[datetime]) -> bool:
    if dt_end is None:
        return br.start <= dt and dt <= br.end
    dt_start = dt
    return br.start <= dt_end and dt_start <= br.end


def filter_dt(block_ranges: list[BlockRange], dt: datetime, dt_end: Optional[datetime]) -> list[BlockRange]:
    return [br for br in block_ranges if block_range_contains(br, dt, dt_end)]


def br_with_span(br: BlockRange) -> str:
    def t(dt):
        return datetime.strftime(dt, "%Y%m%d %H:%M")

    span = str(br.end - br.start)
    return f"BR({br.blknum}, {t(br.start)}..{t(br.end)})  {span}"


def stats(brs: list[BlockRange], dt: datetime, dt_end: Optional[datetime], num_rows: int):
    rel_brs = filter_dt(brs, dt, dt_end)
    print(
        f"num relevant block ranges: {len(rel_brs)}. {len(rel_brs)/len(brs)*100:.1f}% (of {len(brs)})"
    )
    if len(rel_brs) <= num_rows:
        for br in rel_brs:
            print(br_with_span(br))
    else:
        half_rows = int(math.ceil(num_rows / 2))
        print(f"-> first {half_rows}:")
        for br in rel_brs[:half_rows]:
            print(br_with_span(br))
        print(f"-> last {half_rows}:")
        for br in rel_brs[-half_rows:]:
            print(br_with_span(br))


#%%
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="input", required=True, help="input CSV")
    parser.add_argument(
        "-d",
        required=True,
        dest="datetime",
        type=datetime.fromisoformat,
        help="datetime value to search for",
    )
    parser.add_argument(
        "-d2",
        dest="datetime_end",
        type=datetime.fromisoformat,
        help="if given, do a range/between search from -d to -d2",
    )
    parser.add_argument(
        "-n",
        dest="num_rows",
        default=30,
        type=int,
        help="number of block ranges to show",
    )
    args = parser.parse_args()
    brs = parse_csv_file(args.input)
    stats(brs, args.datetime, args.datetime_end, args.num_rows)
