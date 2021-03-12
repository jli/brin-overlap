#%%
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

from brin_parser import BlockRange


# TODO: more than datetime..
@dataclass
class BrinOverlap:
    min_val: datetime
    max_val: datetime
    total: int
    levels: list[list[BlockRange]]


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
    bro = BrinOverlap(datetime.max, datetime.min, 0, [])
    # maybe sort by block range size?
    for i, br in enumerate(block_ranges):
        if i % 5000 == 0:
            logging.info(f'adding row {i} {i/len(block_ranges)*100:.1f}%')
        bro.min_val = min(bro.min_val, br.start)
        bro.max_val = max(bro.max_val, br.end)
        bro.total += 1
        for level in bro.levels:
            if try_insert(level, br):
                break
        else:
            bro.levels.append([br])  # new level
    return bro


def print_bro(bro: BrinOverlap):
    print("BrinOverlap min:", bro.min_val)
    print("            max:", bro.max_val)
    print("     num levels:", len(bro.levels))
    for i, level in enumerate(bro.levels, 1):
        print(f"{i}:", [br.blknum for br in level])
