#!/usr/bin/env python3
"""
Flight Deal Monitor — daily entry point.
Checks Delta nonstop MSP→DFW prices for upcoming ISD 833 school breaks
and sends email alerts when deals are found.
"""

import logging
import sys
from calendar_data import get_upcoming_windows
from flight_checker import search_flights
from price_tracker import record_price, is_deal, already_alerted_today, mark_alerted
from notifier import send_deal_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("main")


def run():
    windows = get_upcoming_windows()
    if not windows:
        log.info("No upcoming travel windows in the next 90 days")
        return

    log.info("Checking %d travel windows", len(windows))

    for depart_date, return_date in windows:
        results = search_flights(depart_date, return_date)
        if not results:
            log.info("No results for %s → %s", depart_date, return_date)
            continue

        # Record the cheapest option
        cheapest = min(results, key=lambda r: r["per_person_price"])
        pp = cheapest["per_person_price"]
        total = cheapest["total_price"]

        record_price(depart_date, return_date, total, pp)
        log.info(
            "%s→%s: cheapest $%.0f/person ($%.0f total)",
            depart_date, return_date, pp, total,
        )

        # Check for deals
        deal, reason = is_deal(depart_date, return_date, pp)
        if deal and not already_alerted_today(depart_date, return_date):
            log.info("DEAL FOUND: %s", reason)
            send_deal_alert(depart_date, return_date, pp, total, reason)
            mark_alerted(depart_date, return_date, pp)
        elif deal:
            log.info("Deal detected but already alerted today — skipping")


if __name__ == "__main__":
    run()
