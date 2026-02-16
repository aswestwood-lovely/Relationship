from __future__ import annotations
from datetime import date, timedelta
from typing import List, Tuple

def month_grid(year: int, month: int) -> Tuple[date, date, List[List[date]]]:
    first = date(year, month, 1)
    if month == 12:
        last = date(year+1, 1, 1) - timedelta(days=1)
    else:
        last = date(year, month+1, 1) - timedelta(days=1)

    # Start on Sunday
    start = first - timedelta(days=(first.weekday()+1) % 7)
    end = last + timedelta(days=(6 - ((last.weekday()+1) % 7)))
    weeks: List[List[date]] = []
    cur = start
    while cur <= end:
        week = [cur + timedelta(days=i) for i in range(7)]
        weeks.append(week)
        cur = cur + timedelta(days=7)
    return first, last, weeks
