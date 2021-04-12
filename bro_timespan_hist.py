#!/usr/bin/env python3
#%%

"""What's the distribution of the block range time span?"""

import argparse
import logging
from datetime import datetime
from typing import Optional

from matplotlib import pyplot as plt

import brin_filenames
from brin_lib import BlockRange
from brin_parser import parse_csv_file


def plot_span_hist(
    brs: list[BlockRange],
    outfile: Optional[str],
    log: bool,
    xlim: Optional[float],
    ylim: Optional[float],
) -> None:
    deltas = (br.end - br.start for br in brs)
    hours = [d.total_seconds() / 3600 for d in deltas]
    plt.hist(hours, 50, log=log)
    plt.title("distribution of block range time spans")
    plt.xlabel("block range end - start (hours)")
    if xlim:
        plt.xlim(0, xlim)
    if ylim:
        plt.ylim(top=ylim)
    if outfile:
        plt.savefig(outfile)


#%%
if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-i", dest="input", required=True, help="input path to CSV")
    p.add_argument("-o", dest="output", help="output path for histogram")
    p.add_argument(
        "-after",
        type=datetime.fromisoformat,
        help="Filter out BRs after this point.",
    )
    p.add_argument(
        "-l", dest="log", action="store_true", default=False, help="use log scale"
    )
    p.add_argument("-x", dest="xlim", type=float, help="set x limit")
    p.add_argument("-y", dest="ylim", type=float, help="set y limit")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO)
    brs = parse_csv_file(args.input, start=args.after)
    outfile = args.output or brin_filenames.timespan_hist_from_brinexport_csv(
        args.input, args.after
    )
    logging.info(f"writing timespan histogram to {outfile}")
    plot_span_hist(brs, outfile, args.log, args.xlim, args.ylim)
