"""Helper for automatically determining filenames."""

import os
import re
from dataclasses import dataclass
from typing import Optional

# For trimming "_YYYYMMDD_HHMMSS" bits.
YYYYMMDD_HHMMSS_RE = re.compile(r"_20\d{2}[01]\d[0123]\d_[012]\d[012345]\d[012345]\d")


@dataclass
class _PathParts:
    dirname: str
    base: str  # basename without ext
    ext: str  # like ".csv" or ".json"


def _get_pathparts(inpath: str, expected_ext: Optional[str]=None) -> _PathParts:
    dirname, inbasename = os.path.dirname(inpath), os.path.basename(inpath)
    inbase, inext = os.path.splitext(inbasename)
    inext = inext.lower()
    if expected_ext and inext != expected_ext:
        raise ValueError(f"input path {inpath} didn't have expected extension {expected_ext}")
    return _PathParts(dirname, inbase, inext.lower())



def _drop_date(s: str) -> str:
    return YYYYMMDD_HHMMSS_RE.sub("", s)


def _check_exists(path: str):
    if os.path.exists(path):
        raise ValueError(f"inferred output path already exists: {path}")


def overlap_json_from_brinexport_csv(brinexport_csv: str) -> str:
    pathparts = _get_pathparts(brinexport_csv, ".csv")
    outbase = pathparts.base.replace("brinexport_", "overlap_")
    outbase = _drop_date(outbase)
    outpath = os.path.join(pathparts.dirname, outbase + ".json")
    _check_exists(outpath)
    return outpath


def viz_svg_from_overlap_json(overlap_json: str) -> str:
    pathparts = _get_pathparts(overlap_json, ".json")
    outbase = pathparts.base.replace("overlap_", "vizoverlap_")
    outpath = os.path.join(pathparts.dirname, outbase + ".svg")
    _check_exists(outpath)
    return outpath


def viz_svg_from_brinexport_csv(brinexport_csv: str) -> str:
    pathparts = _get_pathparts(brinexport_csv, ".csv")
    outbase = pathparts.base.replace("brinexport_", "vizoverlap_")
    outpath = os.path.join(pathparts.dirname, outbase + ".svg")
    _check_exists(outpath)
    return outpath
