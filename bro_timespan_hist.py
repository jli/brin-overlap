#!/usr/bin/env python3
#%%

"""What's the distribution of the block range time span?"""

import argparse
from typing import Optional
from brin_parser import BlockRange
from matplotlib import pyplot as plt

from brin_parser import parse_csv_file


def plot_span_hist(brs: list[BlockRange], outfile: Optional[str] = None):
    deltas = (br.end - br.start for br in brs)
    hours = [d.total_seconds() / 3600 for d in deltas]
    plt.hist(hours, 30, log=True)
    plt.title("distribution of block range time spans")
    plt.xlabel("hours")
    if outfile:
        plt.savefig(outfile)


def main(filepath: str, outfile: Optional[str]):
    brs = parse_csv_file(filepath)
    plot_span_hist(brs, outfile)


#%%
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('-i', dest="input", required=True, help="input path to CSV")
    p.add_argument('-o', dest="output", required=True, help="output path for histogram")
    args = p.parse_args()
    main(args.input, args.output)
