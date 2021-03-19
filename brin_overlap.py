#!/usr/bin/env python3
#%%

"""Compute BrinOverlap object from list of BlockRanges."""

from __future__ import annotations

import argparse
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from dataclasses_json import dataclass_json

import brin_filenames
from brin_lib import BlockRange
from brin_parser import parse_csv_file


# NOTE: there's some kooky timezone stuff happening when round-tripping JSON...
@dataclass_json
@dataclass
class BrinOverlap:
    min_val: datetime
    max_val: datetime
    min_blknum: int
    max_blknum: int
    levels: list[list[BlockRange]]

    @staticmethod
    def initialize(br: BlockRange) -> BrinOverlap:
        return BrinOverlap(br.start, br.end, br.blknum, br.blknum, [[br]])


def read_overlap_file(filepath: str) -> BrinOverlap:
    with open(filepath) as f:
        return BrinOverlap.from_json(f.read())  # type: ignore


def write_overlap_file(bro: BrinOverlap, path: str):
    with open(path, "w") as f:
        f.write(bro.to_json(indent=1))  # type: ignore
        f.write("\n")


def find_position(xs: list[BlockRange], x: BlockRange) -> Optional[int]:
    """Returns index i in xs where x can be inserted (in between existing
    elements xs[i-1] and xs[i]."""
    # We binsearch for a valid spot based on just the start time, and
    # then check that the position is fully valid (considering end time).
    # search range is [lo, hi). code based on Python bisect.bisect_right.
    lo, hi = 0, len(xs)
    while lo < hi:
        mid = (hi + lo) // 2
        x_mid = xs[mid]
        if x.start < x_mid.start:
            hi = mid
        else:
            lo = mid + 1
    # lo is the candidate position.
    left_neighbor = xs[lo - 1] if lo - 1 >= 0 else None
    right_neighbor = xs[lo] if lo < len(xs) else None
    if (left_neighbor is None or left_neighbor.end <= x.start) and (
        right_neighbor is None or x.end <= right_neighbor.start
    ):
        return lo
    return None


def try_insert(level: list[BlockRange], br: BlockRange) -> bool:
    pos = find_position(level, br)
    if pos is None:
        return False
    level.insert(pos, br)
    return True


def compute_overlap(block_ranges: list[BlockRange]) -> BrinOverlap:
    bro: Optional[BrinOverlap] = None
    # maybe sort by block range size?
    for i, br in enumerate(block_ranges):
        if i % 5000 == 0:
            logging.info(f"adding block range {i} {i/len(block_ranges)*100:.1f}%")
        if bro is None:
            bro = BrinOverlap.initialize(br)
            continue
        bro.min_val = min(bro.min_val, br.start)
        bro.max_val = max(bro.max_val, br.end)
        bro.min_blknum = min(bro.min_blknum, br.blknum)
        bro.max_blknum = max(bro.max_blknum, br.blknum)
        for level in bro.levels:
            if try_insert(level, br):
                break
        else:
            bro.levels.append([br])  # new level
    if bro is None:
        raise ValueError("block_ranges was empty, couldn't compute BrinOverlap")
    return bro


def print_bro(bro: BrinOverlap):
    print("BrinOverlap min:", bro.min_val)
    print("            max:", bro.max_val)
    print("     num levels:", len(bro.levels))
    for i, level in enumerate(bro.levels, 1):
        print(f"{i}:", [br.blknum for br in level])


#%%
if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    p = argparse.ArgumentParser()
    p.add_argument("-i", dest="input", required=True, help="input CSV")
    p.add_argument("-o", dest="output", help="output JSON (cached BrinOverlap data)")
    args = p.parse_args()
    output = args.output or brin_filenames.overlap_json_from_brinexport_csv(args.input)
    brs = parse_csv_file(args.input)
    logging.info("computing overlap...")
    overlap = compute_overlap(brs)
    logging.info(f"saving to {output}...")
    write_overlap_file(overlap, output)
    logging.info("done✨")
