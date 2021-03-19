from datetime import datetime

from dataclasses_json import dataclass_json
from dataclasses import dataclass


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
