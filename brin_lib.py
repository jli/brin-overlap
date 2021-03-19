from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class BlockRange:
    blknum: int
    start: datetime
    end: datetime

    def __repr__(self):
        def t(dt):
            return dt.strftime("%Y%m%d %H:%M:%S")

        return f"BR({self.blknum}, {t(self.start)}..{t(self.end)})"


def fully_within_dates(
    br: BlockRange, start: Optional[datetime], end: Optional[datetime]
) -> bool:
    """Test that the block range is fully contained within start and end.
    Useful for filtering out data for a smaller view."""
    return (start is None or start <= br.start) and (end is None or br.end <= end)


def overlaps_dates(
    br: BlockRange, start: Optional[datetime], end: Optional[datetime]
) -> bool:
    """Test that the block range overlaps the start and end given. This will
    return more values than fully_within_dates, as partial overlaps also
    match."""
    return (start is None or start <= br.end) and (end is None or br.start <= end)


def date_match(
    br: BlockRange,
    match_type: Literal["overlap", "within"],
    start: Optional[datetime],
    end: Optional[datetime],
) -> bool:
    if match_type == "overlap":
        return overlaps_dates(br, start, end)
    return fully_within_dates(br, start, end)
