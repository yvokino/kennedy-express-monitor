"""
Kennedy Express Lane Status Scraper
Scrapes expresschi.com every 15 minutes via GitHub Actions.
Logs direction, travel time, speed, and congestion to a CSV.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os
import sys
import re

URL = "https://expresschi.com/"
CSV_FILE = "data/kennedy_express_log.csv"
HEADERS = [
    "timestamp",
    "direction",
    "travel_time",
    "speed_mph",
    "congestion_level",
    "speed_vs_local",
    "raw_html_snippet",
]


def ensure_csv_exists():
    """Create the CSV file with headers if it doesn't exist."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
        print(f"Created new CSV: {CSV_FILE}")


def scrape_express_lane():
    """Fetch expresschi.com and parse the lane status."""
    try:
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"ERROR: Failed to fetch {URL}: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator="\n", strip=True)

    # Parse direction
    direction = "unknown"
    dir_match = re.search(r"Direction\s*[:\n]\s*(Inbound|Outbound|Closed)", text, re.IGNORECASE)
    if dir_match:
        direction = dir_match.group(1).strip()

    # Parse travel time
    travel_time = "unavailable"
    time_match = re.search(r"Travel Time\s*[:\n]\s*(\d+\s*minutes?|Data unavailable)", text, re.IGNORECASE)
    if time_match:
        travel_time = time_match.group(1).strip()

    # Parse speed
    speed_mph = "unavailable"
    speed_match = re.search(r"Speed\s*[:\n]\s*(\d+)\s*MPH", text, re.IGNORECASE)
    if speed_match:
        speed_mph = speed_match.group(1).strip()

    # Parse congestion level
    congestion = "unknown"
    for level in ["Uncongested", "Light", "Moderate", "Heavy", "Closed"]:
        if level.lower() in text.lower():
            congestion = level
            break

    # Parse speed vs local
    speed_vs_local = "unavailable"
    vs_local_match = re.search(r"(\d+)\s*MPH\s*(faster|slower)\s*than\s*Local", text, re.IGNORECASE)
    if vs_local_match:
        diff = vs_local_match.group(1)
        direction_vs = vs_local_match.group(2).lower()
        speed_vs_local = f"{'+' if direction_vs == 'faster' else '-'}{diff} MPH"

    # Keep a short snippet of raw text for debugging
    raw_snippet = text[:300].replace("\n", " | ")

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    return {
        "timestamp": timestamp,
        "direction": direction,
        "travel_time": travel_time,
        "speed_mph": speed_mph,
        "congestion_level": congestion,
        "speed_vs_local": speed_vs_local,
        "raw_html_snippet": raw_snippet,
    }


def append_to_csv(data):
    """Append a row of data to the CSV log."""
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([data[h] for h in HEADERS])
    print(f"Logged: {data['timestamp']} | {data['direction']} | {data['speed_mph']} MPH | {data['congestion_level']}")


def main():
    ensure_csv_exists()
    data = scrape_express_lane()
    if data:
        append_to_csv(data)
        print("Scrape successful.")
    else:
        # Log a failure row so we know the scrape was attempted
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        failure_row = {h: "SCRAPE_FAILED" for h in HEADERS}
        failure_row["timestamp"] = timestamp
        append_to_csv(failure_row)
        print("Scrape failed — logged failure row.")
        sys.exit(1)


if __name__ == "__main__":
    main()
