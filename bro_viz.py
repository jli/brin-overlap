#!/usr/bin/env python3

"""Render SVG of BRIN overlaps"""

import argparse
import logging

import brin_filenames
import brin_overlap
import brin_parser
from brin_viz import DEFAULT_WIDTH, DEFAULT_COLORMAP, DEFAULT_NUM_TICKS, svg


def main(args):
    logging.basicConfig(level=logging.INFO)

    if args.input.lower().endswith("csv"):
        overlap_path = brin_filenames.overlap_json_from_brinexport_csv(args.input)
        logging.info("reading input CSV...")
        block_ranges = brin_parser.parse_csv_file(args.input)
        logging.info("computing overlap...")
        overlap = brin_overlap.compute_overlap(block_ranges)
        logging.info(f"(saving overlap to {overlap_path}...)")
        brin_overlap.write_overlap_file(overlap, overlap_path)
    elif args.input.lower().endswith("json"):
        overlap_path = args.input
        logging.info("reading input JSON...")
        overlap = brin_overlap.read_overlap_file(args.input)
    else:
        raise ValueError(f"-i input file <{args.input}> must be csv or json")

    outfile = args.output or brin_filenames.viz_svg_from_overlap_json(overlap_path)
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
        default=DEFAULT_NUM_TICKS,
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
    args = parser.parse_args()
    main(args)
