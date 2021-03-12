#%%
from datetime import datetime
from typing import Optional

import drawSvg as draw
from matplotlib import colors
from matplotlib import cm

from brin_overlap import BrinOverlap
from brin_parser import BlockRange

DEFAULT_WIDTH = 5000
DEFAULT_NUM_TICKS = 50
DEFAULT_BLOCK_HEIGHT = 8
DEFAULT_COLORMAP = "RdYlGn"
HGAP = 2  # gap between blocks on the same level
VGAP = 2  # gap between levels
CANVAS_MARGIN = 20
DATE_FONT_SIZE = 8


def svg(
    bro: BrinOverlap,
    outfile: Optional[str] = None,
    width: float = DEFAULT_WIDTH,
    block_height: float = DEFAULT_BLOCK_HEIGHT,
    num_ticks: int = DEFAULT_NUM_TICKS,
    colormap: Optional[str] = DEFAULT_COLORMAP,
):
    full_width = width
    del width  # avoid confusion
    # without margin, the bottom stroke border looks funky for some reason.
    full_height = block_height * len(bro.levels) + CANVAS_MARGIN * 2
    d = draw.Drawing(full_width, full_height)
    # area for main drawing
    canvas_width = full_width - CANVAS_MARGIN * 2
    canvas_height = full_height - CANVAS_MARGIN * 2
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
            color = (
                colors.to_hex(cmap(br.blknum / 128 / bro.total))
                if cmap
                else "lightgrey"
            )
            r = draw.Rectangle(*xywh(br, num_level), fill=color, stroke="black")
            d.append(r)

    # draw time ticks
    for dt in datetime_range(bro.min_val, bro.max_val, num_ticks):
        text = [dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")]
        x = interpx(dt) + CANVAS_MARGIN
        # x - 18 to center under tick (hack)
        # y = font size because multi-line string.
        d.append(draw.Text(text, DATE_FONT_SIZE, x - 18, DATE_FONT_SIZE))
        # -7 is magic number (hack)
        d.append(draw.Line(x, CANVAS_MARGIN, x, CANVAS_MARGIN - 7, stroke='black'))

    if outfile:
        print(f"saving to {outfile}")
        d.saveSvg(outfile)
    return d


def datetime_range(start: datetime, end: datetime, num_points: int) -> list[datetime]:
    total_span = end - start
    interval_span = total_span / (num_points - 1)
    ptr = start
    res = []
    for _ in range(1, num_points + 1):
        res.append(ptr)
        ptr += interval_span
    return res
