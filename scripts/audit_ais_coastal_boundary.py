#!/usr/bin/env python3
"""Audit NMD AIS boundary rejections from archived sample aggregates.

This is descriptive QA, not a correction of accepted AIS traffic.
Usage: python scripts/audit_ais_coastal_boundary.py
"""
import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("data/ais_probe"))
    parser.add_argument("--start", type=date.fromisoformat, default=date(2026, 10, 22))
    parser.add_argument("--end", type=date.fromisoformat, default=date(2026, 11, 4))
    args = parser.parse_args()
    totals = Counter()
    classifications = Counter()
    samples = []
    skipped = []
    for path in sorted(args.root.rglob("*.json")):
        try:
            sample = json.loads(path.read_text(encoding="utf-8"))
            stamp = sample.get("sample_started_utc")
            if not stamp:
                continue
            day = date.fromisoformat(stamp[:10])
            if not args.start <= day <= args.end:
                continue
            if sample.get("geographic_filter") != "lulea_nmd_marine_v1":
                skipped.append({"path": str(path), "reason": "not an NMD sample"})
                continue
            rejected = sample.get("rejected_message_counts") or {}
            if "outside_marine_polygon" not in rejected:
                skipped.append({"path": str(path), "reason": "missing rejection aggregate"})
                continue
            outside = int(rejected["outside_marine_polygon"])
            near = int(rejected.get("outside_within_30m", 0))
            if outside < 0 or near < 0 or near > outside:
                raise ValueError("inconsistent counts")
            beyond = outside-near
            totals.update({"outside": outside, "outside_near_30m": near,
                           "outside_beyond_30m": beyond})
            classifications[sample.get("quality_summary", "unknown")] += 1
            samples.append({"timestamp_utc": stamp, "outside": outside,
                            "outside_near_30m": near, "outside_beyond_30m": beyond,
                            "quality_summary": sample.get("quality_summary", "unknown")})
        except (ValueError, UnicodeError, TypeError) as exc:
            skipped.append({"path": str(path), "reason": str(exc)})
    outside = totals["outside"]
    result = {
        "period_inclusive": [str(args.start), str(args.end)],
        "samples_with_rejection_aggregates": len(samples),
        "excluded_or_unavailable": skipped,
        "rejected_messages": dict(totals),
        "share_of_rejected_messages_within_30m_pct":
            round(100*totals["outside_near_30m"]/outside, 2) if outside else None,
        "quality_summary_sample_counts": dict(classifications),
        "largest_boundary_rejection_samples": sorted(samples,
            key=lambda x: (-x["outside_near_30m"], x["timestamp_utc"]))[:10],
        "limitations": [
            "Counts are AIS messages, not unique vessels or validated locations.",
            "Outside-within-30m indicates distance from polygon boundary, not confirmed false rejection.",
            "The archive lacks rejected point coordinates; spatial precision cannot be independently validated.",
            "Only samples with rejection aggregates are included; missing samples are not presumed zero.",
            "30 metres is an inspection buffer in EPSG:3006, not a measured GPS uncertainty.",
        ],
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
