#!/usr/bin/env python3
#%%
from __future__ import annotations
from typing import Optional

"""Compute BrinOverlap object from list of BlockRanges."""

import argparse
import logging
from dataclasses import dataclass
from datetime import datetime

from dataclasses_json import dataclass_json

from brin_parser import BlockRange, parse_csv_file


# NOTE: there's some kooky timezone stuff happening when round-tripping JSON...
@dataclass_json
@dataclass
class BrinOverlap:
    # TODO: more than datetime..
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


def fits_in_between(br: BlockRange, br0: BlockRange, br1: BlockRange) -> bool:
    return br0.end <= br.start and br.end <= br1.start


def try_insert(level: list[BlockRange], br: BlockRange) -> bool:
    if not level:
        level.append(br)
        return True
    if br.end <= level[0].start:
        level.insert(0, br)
        return True
    if level[-1].end <= br.start:
        level.append(br)
        return True
    for i, (br0, br1) in enumerate(zip(level, level[1:])):
        if fits_in_between(br, br0, br1):
            level.insert(i + 1, br)
            return True
    return False


def compute_overlap(block_ranges: list[BlockRange]) -> BrinOverlap:
    bro: Optional[BrinOverlap] = None
    # maybe sort by block range size?
    for i, br in enumerate(block_ranges):
        if i % 5000 == 0:
            logging.info(f"adding row {i} {i/len(block_ranges)*100:.1f}%")
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
    p.add_argument(
        "-o", dest="output", required=True, help="output JSON (cached BrinOverlap data)"
    )
    args = p.parse_args()
    brs = parse_csv_file(args.input)
    logging.info("computing overlap...")
    overlap = compute_overlap(brs)
    logging.info(f"saving to {args.output}...")
    with open(args.output, "w") as f:
        f.write(overlap.to_json(indent=1))  # type: ignore
        f.write("\n")
    logging.info("done✨")
