"""
ISD 833 (South Washington County) 2025-2026 school calendar.
Each travel window is a list of (depart_date, return_date) tuples.
"""

from datetime import date, timedelta

TRAVEL_WINDOWS = [
    # Fall Break — Oct 16-17 off → Thu-Sun trip
    (date(2025, 10, 16), date(2025, 10, 19)),

    # Thanksgiving — Nov 26-28 off → Wed-Sun
    (date(2025, 11, 26), date(2025, 11, 30)),

    # Winter Break — Dec 22 - Jan 2 → two options
    (date(2025, 12, 20), date(2025, 12, 28)),  # Christmas week
    (date(2025, 12, 27), date(2026, 1, 3)),     # New Year's week

    # MLK Day — Jan 19 off → Fri-Mon
    (date(2026, 1, 16), date(2026, 1, 19)),

    # Presidents' Day — Feb 16 off → Fri-Mon
    (date(2026, 2, 13), date(2026, 2, 16)),

    # Spring Break — Mar 6-13 off → full week
    (date(2026, 3, 6), date(2026, 3, 13)),

    # Summer — Jun 5 to ~Sep 1: sample 5 representative weeks
    (date(2026, 6, 12), date(2026, 6, 19)),   # mid-June
    (date(2026, 6, 26), date(2026, 7, 3)),     # late June/July 4th
    (date(2026, 7, 10), date(2026, 7, 17)),    # mid-July
    (date(2026, 7, 31), date(2026, 8, 7)),     # late July/early Aug
    (date(2026, 8, 14), date(2026, 8, 21)),    # mid-August
]


def get_upcoming_windows(lookahead_days=90):
    """Return travel windows within the lookahead period from today."""
    today = date.today()
    cutoff = today + timedelta(days=lookahead_days)
    return [
        (dep, ret)
        for dep, ret in TRAVEL_WINDOWS
        if dep >= today and dep <= cutoff
    ]
