#%%
import logging
from datetime import datetime, timedelta
from typing import Optional

import drawSvg as draw
from matplotlib import cm, colors

from brin_lib import BlockRange
from brin_overlap import BrinOverlap

DEFAULT_WIDTH = 5000
DEFAULT_BLOCK_HEIGHT = 8
DEFAULT_COLORMAP = "RdYlGn"
HGAP = 2  # gap between blocks on the same level
VGAP = 2  # gap between levels
APPROX_DATE_TICK_WIDTH = 60
DATE_FONT_SIZE = 14
CANVAS_MARGIN = DATE_FONT_SIZE * 2.5
TICK_LENGTH = 10  # manually tweaked to look good


def _br_frac(blknum: int, min_blknum: int, max_blknum: int) -> float:
    return (blknum - min_blknum) / (max_blknum - min_blknum)


def _even_datetime_range(
    start: datetime, end: datetime, num_points: int
) -> list[datetime]:
    total_span = end - start
    interval_span = total_span / (num_points - 1)
    ptr = start
    res = []
    for _ in range(1, num_points + 1):
        res.append(ptr)
        ptr += interval_span
    return res


# Note: the auto functions were just tweaked by hand until they looked nice.
# This is a kinda spaghetti, should consider a more principled approach.
def _auto_datetime_range(
    start: datetime, end: datetime, num_points: int
) -> list[datetime]:
    total_span = end - start
    interval = total_span / num_points
    rounded_interval = _round_interval(interval)
    rounded_start = _round_start_time(start, rounded_interval)
    logging.debug(f"autoticks: {total_span=!s}")
    logging.debug(f"autoticks: {interval=!s} => {rounded_interval=!s}")
    logging.debug(f"autoticks: {start=!s} => {rounded_start=!s}")

    # Ensure that dts uses the given start/end time as the first and last value.
    dts = [start]
    ptr = rounded_start + rounded_interval
    # Given multiple levels of rounding, the first tick after start may
    # be too close to the start. Skip it if so.
    if ptr - start < interval / 2:
        ptr += rounded_interval
    while ptr < end:
        dts.append(ptr)
        ptr += rounded_interval
    if end - dts[-1] < interval / 2:
        dts = dts[:-1]
    dts.append(end)
    return dts


def _round_start_time(start: datetime, interval: timedelta) -> datetime:
    """Returns datetime close to start but more "rounded"."""
    if interval >= timedelta(days=1):
        return datetime(start.year, start.month, start.day, tzinfo=start.tzinfo)
    if interval >= timedelta(hours=3):
        nearest_3rd_hour = round(start.hour / 6) * 6
        return datetime(
            start.year, start.month, start.day, nearest_3rd_hour, tzinfo=start.tzinfo
        )
    if interval >= timedelta(hours=1):
        return datetime(
            start.year,
            start.month,
            start.day,
            start.hour,
            tzinfo=start.tzinfo,
        )
    return start


def _round_interval(interval: timedelta) -> timedelta:
    if interval > timedelta(days=1):
        return timedelta(days=interval.days)
    if interval > timedelta(hours=4):
        hours = interval.total_seconds() / 3600
        multiple_of_6h = round(hours / 6) * 6
        return timedelta(hours=multiple_of_6h)
    if interval > timedelta(hours=1.5):
        hours = interval.total_seconds() / 3600
        multiple_of_3h = round(hours / 3) * 3
        return timedelta(hours=multiple_of_3h)
    if interval > timedelta(minutes=15):
        minutes = interval.total_seconds() / 60
        nearest_30_min = round(minutes / 30) * 30
        return timedelta(minutes=nearest_30_min)
    return interval


def _auto_num_ticks(canvas_width: float) -> int:
    num_ticks = int(round(canvas_width / APPROX_DATE_TICK_WIDTH / 1.5))
    return max(num_ticks, 3)


def svg(
    bro: BrinOverlap,
    outfile: Optional[str] = None,
    width: float = DEFAULT_WIDTH,
    block_height: float = DEFAULT_BLOCK_HEIGHT,
    num_ticks: Optional[int] = None,
    colormap: Optional[str] = DEFAULT_COLORMAP,
) -> draw.Drawing:
    full_width = width
    del width  # avoid confusion
    # without margin, the bottom stroke border looks funky for some reason.
    full_height = block_height * len(bro.levels) + CANVAS_MARGIN * 2
    d = draw.Drawing(full_width, full_height)
    # area for main drawing
    canvas_width = full_width - CANVAS_MARGIN * 2
    canvas_height = full_height - CANVAS_MARGIN * 2
    # draw border around block range rectangles
    d.append(
        draw.Rectangle(
            CANVAS_MARGIN,
            CANVAS_MARGIN,
            canvas_width,
            canvas_height,
            fill="none",
            stroke="black",
            stroke_width=2,
        )
    )

    def interpx(dt: datetime) -> float:
        val_range = bro.max_val - bro.min_val
        return (dt - bro.min_val) / val_range * canvas_width

    def xywh(br: BlockRange, num_level: int) -> tuple[float, float, float, float]:
        x = interpx(br.start)
        w = interpx(br.end) - x
        y = num_level * block_height
        h = block_height
        # w can be < HGAP when there are many blocks / insufficient canvas
        # width, so use max to ensure visibility.
        res = (x + CANVAS_MARGIN, y + CANVAS_MARGIN, max(2, w - HGAP), h - VGAP)
        # print(res)
        return res

    # draw block ranges
    cmap = cm.get_cmap(colormap) if colormap else None
    for num_level, level in enumerate(bro.levels):
        for br in level:
            p = _br_frac(br.blknum, bro.min_blknum, bro.max_blknum)
            color = colors.to_hex(cmap(p)) if cmap else "lightgrey"
            r = draw.Rectangle(*xywh(br, num_level), fill=color, stroke="black")
            d.append(r)

    # draw time ticks
    if num_ticks is None:
        datetime_range = _auto_datetime_range(
            bro.min_val, bro.max_val, _auto_num_ticks(canvas_width)
        )
    else:
        datetime_range = _even_datetime_range(bro.min_val, bro.max_val, num_ticks)
    prev_date = None
    for dt in datetime_range:
        # text = []
        # if prev_date != dt.date():
        #     text.append(dt.strftime("%Y-%m-%d"))
        # text.append(dt.strftime("%H:%M"))
        text = [
            "" if prev_date == dt.date() else dt.strftime("%Y-%m-%d"),
            dt.strftime("%H:%M"),
        ]
        prev_date = dt.date()
        x = interpx(dt) + CANVAS_MARGIN
        # y = font size because multi-line string.
        d.append(draw.Text(text, DATE_FONT_SIZE, x, DATE_FONT_SIZE, center=True))
        d.append(
            draw.Line(x, CANVAS_MARGIN, x, CANVAS_MARGIN - TICK_LENGTH, stroke="black")
        )

    if outfile:
        print(f"saving to {outfile}")
        d.saveSvg(outfile)
    return d
