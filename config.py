import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

# SerpAPI
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

# SMTP email settings
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
ALERT_TO = os.getenv("ALERT_TO", SMTP_USER)

# Flight search parameters
ORIGIN = "MSP"
DESTINATION = "DFW"
AIRLINE = "Delta"  # SerpAPI airline filter
ADULTS = 2
CHILDREN = 2

# Deal detection
ABSOLUTE_THRESHOLD = 250  # per-person price in USD
RELATIVE_DROP_PCT = 0.15  # 15% below median
MIN_DATA_POINTS = 7       # need this many before relative detection kicks in

# Database
DB_PATH = Path(__file__).parent / "flights.db"
