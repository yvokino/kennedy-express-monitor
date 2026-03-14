"""
Kennedy Express Lane — Pattern Analysis
Run this after 1-2 weeks of data collection to see open/close patterns.

Usage:
    python analyze.py                         # analyze the default CSV
    python analyze.py path/to/custom.csv      # analyze a specific CSV
"""

import csv
import sys
from datetime import datetime
from collections import defaultdict


def load_data(csv_path="data/kennedy_express_log.csv"):
    """Load the scraped data from CSV."""
    rows = []
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["direction"] == "SCRAPE_FAILED":
                continue
            try:
                row["dt"] = datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S UTC")
            except ValueError:
                continue
            rows.append(row)
    return rows


def analyze_patterns(rows):
    """Analyze the express lane direction patterns."""

    print("=" * 65)
    print("  KENNEDY EXPRESS LANE — STATUS PATTERN REPORT")
    print("=" * 65)

    if not rows:
        print("\nNo data found. Make sure the scraper has been running.")
        return

    # --- Basic stats ---
    first = rows[0]["dt"]
    last = rows[-1]["dt"]
    total_days = (last - first).days + 1
    print(f"\nData range : {first.strftime('%Y-%m-%d %H:%M')} → {last.strftime('%Y-%m-%d %H:%M')}")
    print(f"Total rows : {len(rows)}")
    print(f"Days span  : {total_days}")

    # --- Direction distribution ---
    dir_counts = defaultdict(int)
    for r in rows:
        dir_counts[r["direction"].lower()] += 1
    print(f"\n--- Direction Distribution ---")
    for d, c in sorted(dir_counts.items(), key=lambda x: -x[1]):
        pct = c / len(rows) * 100
        print(f"  {d:<12s}  {c:>5d} readings  ({pct:.1f}%)")

    # --- Hourly pattern (what direction is most common at each hour?) ---
    hour_dir = defaultdict(lambda: defaultdict(int))
    for r in rows:
        hour = r["dt"].hour
        hour_dir[hour][r["direction"].lower()] += 1

    print(f"\n--- Typical Direction by Hour of Day (UTC) ---")
    print(f"  {'Hour':<8s}  {'Direction':<12s}  {'Confidence':<12s}")
    print(f"  {'----':<8s}  {'---------':<12s}  {'----------':<12s}")
    for h in range(24):
        if h in hour_dir:
            counts = hour_dir[h]
            total = sum(counts.values())
            dominant = max(counts, key=counts.get)
            confidence = counts[dominant] / total * 100
            bar = "█" * int(confidence / 5)
            print(f"  {h:02d}:00     {dominant:<12s}  {confidence:5.1f}%  {bar}")
        else:
            print(f"  {h:02d}:00     {'no data':<12s}")

    # --- Day-of-week pattern ---
    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow_dir = defaultdict(lambda: defaultdict(int))
    for r in rows:
        dow = r["dt"].weekday()
        dow_dir[dow][r["direction"].lower()] += 1

    print(f"\n--- Direction Pattern by Day of Week ---")
    for d in range(7):
        if d in dow_dir:
            counts = dow_dir[d]
            total = sum(counts.values())
            summary = ", ".join(
                f"{k}: {v / total * 100:.0f}%" for k, v in sorted(counts.items(), key=lambda x: -x[1])
            )
            print(f"  {day_names[d]:<12s}  ({total:>3d} readings)  {summary}")

    # --- Transition detection (when does direction change?) ---
    print(f"\n--- Detected Direction Transitions ---")
    transitions = []
    for i in range(1, len(rows)):
        prev_dir = rows[i - 1]["direction"].lower()
        curr_dir = rows[i]["direction"].lower()
        if prev_dir != curr_dir:
            transitions.append({
                "from": prev_dir,
                "to": curr_dir,
                "time": rows[i]["dt"],
            })

    if transitions:
        # Summarize typical transition times
        trans_times = defaultdict(list)
        for t in transitions:
            key = f"{t['from']} → {t['to']}"
            trans_times[key].append(t["time"])

        for key, times in trans_times.items():
            hours = [t.hour + t.minute / 60 for t in times]
            avg_hour = sum(hours) / len(hours)
            h = int(avg_hour)
            m = int((avg_hour - h) * 60)
            print(f"  {key:<28s}  seen {len(times):>3d} times, avg ~{h:02d}:{m:02d} UTC")

        # Show last 10 transitions
        print(f"\n  Last 10 transitions:")
        for t in transitions[-10:]:
            print(f"    {t['time'].strftime('%Y-%m-%d %H:%M')} UTC  :  {t['from']} → {t['to']}")
    else:
        print("  No direction changes detected in the data.")

    # --- Average speed by direction ---
    dir_speeds = defaultdict(list)
    for r in rows:
        try:
            speed = float(r["speed_mph"])
            dir_speeds[r["direction"].lower()].append(speed)
        except (ValueError, TypeError):
            continue

    if dir_speeds:
        print(f"\n--- Average Speed by Direction ---")
        for d, speeds in sorted(dir_speeds.items()):
            avg = sum(speeds) / len(speeds)
            print(f"  {d:<12s}  avg {avg:.1f} MPH  (from {len(speeds)} readings)")

    print(f"\n{'=' * 65}")
    print("  Tip: Times are in UTC. Chicago is UTC-5 (CST) or UTC-6 (CDT).")
    print(f"{'=' * 65}\n")


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/kennedy_express_log.csv"
    rows = load_data(csv_path)
    analyze_patterns(rows)


if __name__ == "__main__":
    main()
