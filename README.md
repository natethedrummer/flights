# Flight Deal Monitor: MSP → DFW

Automatically checks Delta nonstop round-trip prices from Minneapolis (MSP) to Dallas-Fort Worth (DFW) and sends email alerts when deals are found. Searches are scoped to dates when kids are out of school (ISD 833, South Washington County).

## How It Works

1. **Daily at 8 AM**, the monitor checks Google Flights (via SerpAPI) for upcoming school break travel windows
2. Prices are recorded in a local SQLite database to build history
3. A deal alert is emailed when either:
   - Price drops below **$250/person** (absolute threshold)
   - Price drops **15%+ below the median** for that date pair (after 7+ data points)
4. Alerts are deduplicated — you won't get the same deal emailed twice in one day

## Search Parameters

- **Route:** MSP → DFW (nonstop)
- **Airline:** Delta
- **Passengers:** 2 adults, 2 children
- **Trip type:** Round trip

## Travel Windows (ISD 833, 2025-2026)

| Window | Dates |
|--------|-------|
| Fall Break | Oct 16–19 |
| Thanksgiving | Nov 26–30 |
| Winter Break | Dec 20–28 / Dec 27–Jan 3 |
| MLK Day | Jan 16–19 |
| Presidents' Day | Feb 13–16 |
| Spring Break | Mar 6–13 |
| Summer | 5 sampled weeks (Jun–Aug) |

## Setup

### 1. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
```

Edit `.env` with:
- **SERPAPI_KEY** — free at [serpapi.com](https://serpapi.com) (250 searches/month)
- **SMTP_USER / SMTP_PASSWORD** — Gmail address + [App Password](https://myaccount.google.com/apppasswords)
- **ALERT_TO** — email address for alerts

### 3. Test it

```bash
source venv/bin/activate
python main.py
```

Check the console output for price lookups and inspect `flights.db` for recorded prices.

### 4. Schedule daily runs (macOS)

```bash
cp com.user.flightmonitor.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.user.flightmonitor.plist
```

Logs are written to `/tmp/flightmonitor.log` and `/tmp/flightmonitor.err`.

To stop:
```bash
launchctl unload ~/Library/LaunchAgents/com.user.flightmonitor.plist
```

## Project Structure

```
config.py              # API keys, email settings, thresholds
calendar_data.py       # ISD 833 school calendar travel windows
flight_checker.py      # SerpAPI Google Flights integration
price_tracker.py       # SQLite price history + deal detection
notifier.py            # Email alerts via SMTP
main.py                # Orchestrator (daily entry point)
```
