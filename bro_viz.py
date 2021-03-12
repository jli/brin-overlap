#!/usr/bin/env python3

"""Render SVG of BRIN overlaps"""

import argparse
import logging

from brin_overlap import compute_overlap
from brin_parser import parse_csv_rows
from brin_viz import DEFAULT_CANVAS_WIDTH, DEFAULT_COLORMAP, svg


def main(args):
    logging.basicConfig(level=logging.INFO)
    with open(args.input) as f:
        logging.info('reading input...')
        block_ranges = parse_csv_rows(f)
    logging.info('computing overlap...')
    brin_overlap = compute_overlap(block_ranges)
    logging.info('rendering SVG...')
    svg(
        brin_overlap,
        outfile=args.output,
        canvas_width=args.width,
        colormap=args.colormap,
    )
    logging.info('done✨')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", dest="input", required=True, help="input CSV file with brin page items"
    )
    parser.add_argument("-o", dest="output", required=True, help="output SVG file")
    parser.add_argument(
        "-w",
        dest="width",
        type=float,
        default=DEFAULT_CANVAS_WIDTH,
        help="width of SVG",
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
