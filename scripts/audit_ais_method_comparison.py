#!/usr/bin/env python3
"""Audit paired AIS samples without modifying source data.

Usage: python scripts/audit_ais_method_comparison.py
Optional: --csv data/ais_method_comparison/paired_samples.csv
"""
import argparse
import csv
import json
import statistics
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path


def audit(csv_path, start, end):
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    required = ("timestamp_utc", "rectangle_mmsi", "marine_mmsi",
                "rectangle_messages", "marine_messages")
    if rows and any(col not in rows[0] for col in required):
        raise ValueError(f"Missing required columns: {required}")
    paired = []
    excluded = []
    for index, row in enumerate(rows, 2):
        try:
            dt = datetime.fromisoformat(row["timestamp_utc"].replace("Z", "+00:00"))
            if dt.tzinfo is None:
                raise ValueError("timestamp has no timezone")
            day = dt.date()
            if day < start or day > end:
                continue
            vals = {key: int(row[key]) for key in required[1:]}
            if min(vals.values()) < 0:
                raise ValueError("negative count")
            if vals["marine_mmsi"] > vals["rectangle_mmsi"] or vals["marine_messages"] > vals["rectangle_messages"]:
                raise ValueError("marine count exceeds rectangle count")
            paired.append({"timestamp_utc": row["timestamp_utc"], "date": str(day), **vals})
        except (ValueError, KeyError, TypeError) as exc:
            excluded.append({"row": index, "reason": str(exc)})
    def total(k):
        return sum(r[k] for r in paired)
    rec = total("rectangle_mmsi")
    mar = total("marine_mmsi")
    rm = total("rectangle_messages")
    mm = total("marine_messages")
    differences = [r["rectangle_mmsi"] - r["marine_mmsi"] for r in paired]
    pct = [100 * (r["rectangle_mmsi"] - r["marine_mmsi"]) / r["rectangle_mmsi"]
           for r in paired if r["rectangle_mmsi"] > 0]
    days = {r["date"] for r in paired}
    missing_days = []
    day = start
    while day <= end:
        if str(day) not in days:
            missing_days.append(str(day))
        day += timedelta(days=1)
    extremes = sorted(
        [{"timestamp_utc": r["timestamp_utc"],
          "rectangle_mmsi": r["rectangle_mmsi"],
          "marine_mmsi": r["marine_mmsi"],
          "difference": r["rectangle_mmsi"]-r["marine_mmsi"],
          "difference_pct": (100*(r["rectangle_mmsi"]-r["marine_mmsi"])/r["rectangle_mmsi"]
                             if r["rectangle_mmsi"] else None)}
         for r in paired],
        key=lambda x: (-x["difference"], x["timestamp_utc"]))[:10]
    return {
        "period_inclusive": [str(start), str(end)],
        "paired_samples": len(paired),
        "mmsi_per_sample_sums": {"rectangle": rec, "marine": mar,
                                  "difference": rec-mar,
                                  "reduction_pct": round(100*(rec-mar)/rec, 2) if rec else None},
        "message_sums": {"rectangle": rm, "marine": mm, "difference": rm-mm,
                         "reduction_pct": round(100*(rm-mm)/rm, 2) if rm else None},
        "median_mmsi_difference": statistics.median(differences) if differences else None,
        "median_pct_difference_nonzero_rectangle": statistics.median(pct) if pct else None,
        "mean_pct_difference_nonzero_rectangle": round(statistics.mean(pct), 2) if pct else None,
        "difference_distribution": dict(sorted(Counter(differences).items())),
        "zero_both": sum(r["rectangle_mmsi"] == r["marine_mmsi"] == 0 for r in paired),
        "rectangle_positive_marine_zero": sum(r["rectangle_mmsi"] > 0 and r["marine_mmsi"] == 0 for r in paired),
        "sampled_days": len(days),
        "calendar_days_without_paired_samples": missing_days,
        "excluded_csv_rows": excluded,
        "largest_absolute_differences": extremes,
        "limitations": [
            "Per-sample sums of unique MMSI do not represent unique vessels across the period.",
            "A missing calendar day is not proof of a failed scheduled run.",
            "These CSVs alone cannot determine missing scheduled windows or individual vessel positions.",
            "Historical rectangle bounds may differ from bounds used for the paired test.",
        ]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=Path("data/ais_method_comparison/paired_samples.csv"))
    parser.add_argument("--start", type=date.fromisoformat, default=date(2026, 10, 22))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2026, 11, 4))
    args = parser.parse_args()
    print(json.dumps(audit(args.csv, args.start, args.end), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
