"""
Query SerpAPI Google Flights for MSP → DFW nonstop round-trips on Delta.
"""

import logging
from datetime import date
from serpapi import GoogleSearch
import config

log = logging.getLogger(__name__)


def search_flights(depart_date: date, return_date: date) -> list[dict]:
    """
    Search for round-trip flights and return a list of price results.
    Each result dict has keys: price, airline, stops, departure, arrival, duration.
    """
    params = {
        "engine": "google_flights",
        "departure_id": config.ORIGIN,
        "arrival_id": config.DESTINATION,
        "outbound_date": depart_date.isoformat(),
        "return_date": return_date.isoformat(),
        "adults": config.ADULTS,
        "children": config.CHILDREN,
        "currency": "USD",
        "hl": "en",
        "type": "1",       # round trip
        "stops": "1",      # nonstop only
        "include_airlines": "DL",  # Delta
        "api_key": config.SERPAPI_KEY,
    }

    log.info(
        "Searching flights %s→%s  %s to %s",
        config.ORIGIN, config.DESTINATION,
        depart_date, return_date,
    )

    try:
        search = GoogleSearch(params)
        data = search.get_dict()
    except Exception:
        log.exception("SerpAPI request failed")
        return []

    if "error" in data:
        log.error("SerpAPI error: %s", data["error"])
        return []

    results = []
    best = data.get("best_flights", [])
    other = data.get("other_flights", [])

    for itinerary in best + other:
        price = itinerary.get("price")
        if price is None:
            continue

        # Total passengers
        total_pax = config.ADULTS + config.CHILDREN
        per_person = round(price / total_pax, 2)

        legs = itinerary.get("flights", [])
        outbound_info = legs[0] if legs else {}

        results.append({
            "total_price": price,
            "per_person_price": per_person,
            "airline": outbound_info.get("airline", "Delta"),
            "departure_time": outbound_info.get("departure_airport", {}).get("time", ""),
            "arrival_time": outbound_info.get("arrival_airport", {}).get("time", ""),
            "duration_min": outbound_info.get("duration", 0),
        })

    log.info("Found %d itineraries", len(results))
    return results
