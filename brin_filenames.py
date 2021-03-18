"""Helper for automatically determining filenames."""

import os
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional


@dataclass
class _PathParts:
    dirname: str
    base: str  # basename without ext
    ext: str  # like ".csv" or ".json"


def _get_pathparts(inpath: str, expected_ext: Optional[str] = None) -> _PathParts:
    dirname, inbasename = os.path.dirname(inpath), os.path.basename(inpath)
    inbase, inext = os.path.splitext(inbasename)
    inext = inext.lower()
    if expected_ext and inext != expected_ext:
        raise ValueError(
            f"input path {inpath} didn't have expected extension {expected_ext}"
        )
    return _PathParts(dirname, inbase, inext.lower())


def _check_exists(path: str):
    if os.path.exists(path):
        raise ValueError(f"inferred output path already exists: {path}")


def overlap_json_from_brinexport_csv(brinexport_csv: str) -> str:
    pathparts = _get_pathparts(brinexport_csv, ".csv")
    outbase = pathparts.base.replace("brinexport_", "overlap_")
    outpath = os.path.join(pathparts.dirname, outbase + ".json")
    _check_exists(outpath)
    return outpath


def viz_svg_from_overlap_json(overlap_json: str) -> str:
    pathparts = _get_pathparts(overlap_json, ".json")
    outbase = pathparts.base.replace("overlap_", "vizoverlap_")
    outpath = os.path.join(pathparts.dirname, outbase + ".svg")
    _check_exists(outpath)
    return outpath


def _after_part(after: Optional[datetime]) -> str:
    """Return filename component for 'after' filter if present."""
    if after is None:
        return ""
    if after.time() == time.min:
        return after.strftime("_after%Y%m%d")
    else:
        return after.strftime("_after%Y%m%d%H%M%S")


def viz_svg_from_brinexport_csv(brinexport_csv: str, after: Optional[datetime]) -> str:
    pathparts = _get_pathparts(brinexport_csv, ".csv")
    outbase = pathparts.base.replace("brinexport_", "vizoverlap_")
    outpath = os.path.join(pathparts.dirname, outbase + _after_part(after) + ".svg")
    _check_exists(outpath)
    return outpath
