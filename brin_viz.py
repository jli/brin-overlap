#%%
from typing import Optional

import drawSvg as draw
from matplotlib import colors
from matplotlib import cm

from brin_overlap import BrinOverlap
from brin_parser import BlockRange

DEFAULT_CANVAS_WIDTH = 700
DEFAULT_BLOCK_HEIGHT = 8
DEFAULT_COLORMAP = "cool"
HGAP = 2  # gap between blocks on the same level
VGAP = 2  # gap between levels
CANVAS_MARGIN = 15


def svg(
    bro: BrinOverlap,
    outfile: Optional[str] = None,
    width: float = DEFAULT_CANVAS_WIDTH,
    block_height: float = DEFAULT_BLOCK_HEIGHT,
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

    def xywh(br: BlockRange, num_level: int) -> tuple[float, float, float, float]:
        val_range = bro.max_val - bro.min_val
        x = (br.start - bro.min_val) / val_range * canvas_width
        w = (br.end - bro.min_val) / val_range * canvas_width - x
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
            # color = colors.rgb2hex(cmap(i / bro.total)) if cmap else 'lightgrey'
            color = (
                colors.to_hex(cmap(br.blknum / 128 / bro.total))
                if cmap
                else "lightgrey"
            )
            r = draw.Rectangle(*xywh(br, num_level), fill=color, stroke="black")
            d.append(r)

    if outfile:
        print(f"saving to {outfile}")
        d.saveSvg(outfile)
    return d
