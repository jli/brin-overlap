#!/usr/bin/env python3

"""Render SVG of BRIN overlaps"""

import argparse
from datetime import datetime
import logging
from typing import Literal, NamedTuple, Optional, cast

import brin_filenames
import brin_overlap
import brin_parser
from brin_viz import DEFAULT_WIDTH, DEFAULT_COLORMAP, svg


def _v_to_level(i: int) -> int:
    return {0: logging.CRITICAL, 1: logging.INFO, 2: logging.DEBUG}[i]


class Args(NamedTuple):
    input: str
    after: Optional[datetime]
    overlap: Optional[bool]
    output: Optional[str]
    width: float
    num_ticks: Optional[int]
    colormap: Optional[str]
    v: Literal[1, 2, 3]


def main(args: Args) -> None:
    logging.basicConfig(level=_v_to_level(args.v))

    outfile = args.output
    if args.input.lower().endswith("csv"):
        if outfile is None:
            outfile = brin_filenames.viz_svg_from_brinexport_csv(args.input, args.after)
        logging.info("reading input CSV...")
        # By default, use "within" for smaller viz's when filtering with -after.
        match_type: Literal["overlap", "within"] = (
            "overlap" if args.overlap else "within"
        )
        block_ranges = brin_parser.parse_csv_file(
            args.input, start=args.after, match_type=match_type
        )
        logging.info("computing overlap...")
        overlap = brin_overlap.compute_overlap(block_ranges)
        if args.after is None:
            overlap_path = brin_filenames.overlap_json_from_brinexport_csv(args.input)
            logging.info(f"(saving overlap to {overlap_path}...)")
            brin_overlap.write_overlap_file(overlap, overlap_path)
    elif args.input.lower().endswith("json"):
        if args.after is not None:
            raise ValueError("-after only valid for raw CSV input")
        if outfile is None:
            outfile = brin_filenames.viz_svg_from_overlap_json(args.input)
        logging.info("reading input JSON...")
        overlap = brin_overlap.read_overlap_file(args.input)
    else:
        raise ValueError(f"-i input file <{args.input}> must be csv or json")

    logging.info("rendering SVG...")
    svg(
        overlap,
        outfile=outfile,
        width=args.width,
        num_ticks=args.num_ticks,
        colormap=args.colormap,
    )
    logging.info("done✨")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        dest="input",
        required=True,
        help="input CSV of brin page items OR input JSON of BrinOverlap data",
    )
    parser.add_argument(
        "-after",
        type=datetime.fromisoformat,
        help="Only show BRs after this point. Only applicable for CSV input.",
    )
    parser.add_argument(
        "-overlap",
        action="store_true",
        help="Makes -after 'inclusive' - returns blocks that include partial data.",
    )
    parser.add_argument("-o", dest="output", help="output SVG file")
    parser.add_argument(
        "-w",
        dest="width",
        type=float,
        default=DEFAULT_WIDTH,
        help="width of SVG",
    )
    parser.add_argument(
        "-t",
        dest="num_ticks",
        type=int,
        help="number of x-axis time ticks",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-c",
        dest="colormap",
        default=DEFAULT_COLORMAP,
        help="colormap to use (eg viridis, inferno, cool, Wista) https://matplotlib.org/stable/tutorials/colors/colormaps.html#miscellaneous",
    )
    group.add_argument(
        "-nc",
        action="store_const",
        const=None,
        dest="colormap",
        help="disable coloring",
    )
    parser.add_argument(
        "-v", type=int, default=1, choices=[0, 1, 2], help="logging verbosity"
    )
    args = cast(Args, parser.parse_args())
    if args.overlap and args.after is None:
        raise ValueError("must include -after if passing -overlap")
    main(args)
