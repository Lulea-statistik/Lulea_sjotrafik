#!/usr/bin/env python3
"""Compare paired AIS geographic methods for same sample windows."""
import csv,json,statistics
from datetime import datetime,timezone
from pathlib import Path
root=Path(__file__).resolve().parents[1]
start="2026-10-22"
end="2026-11-05"
rows=[]
for file in sorted((root/"data/ais_probe").rglob("*.json")):
    try:d=json.loads(file.read_text(encoding="utf-8"))
    except (ValueError,UnicodeError):continue
    stamp=d.get("sample_started_utc","")
    if not (start <= stamp[:10] < end):continue
    pair=d.get("parallel_comparison")
    if not pair:continue
    old=pair.get("rectangle_unique_mmsi_count",0)
    new=pair.get("marine_unique_mmsi_count",0)
    old_messages=sum(pair.get("rectangle_message_counts",{}).values())
    new_messages=sum(pair.get("marine_message_counts",{}).values())
    rows.append(dict(timestamp_utc=stamp,rectangle_mmsi=old,marine_mmsi=new,delta_mmsi=old-new,delta_mmsi_pct=round((old-new)/old*100,2) if old else None,rectangle_messages=old_messages,marine_messages=new_messages))
out=root/"data/ais_method_comparison"
out.mkdir(parents=True,exist_ok=True)
with (out/"paired_samples.csv").open("w",encoding="utf-8",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=["timestamp_utc","rectangle_mmsi","marine_mmsi","delta_mmsi","delta_mmsi_pct","rectangle_messages","marine_messages"])
    writer.writeheader();writer.writerows(rows)
totold=sum(r["rectangle_mmsi"] for r in rows)
totnew=sum(r["marine_mmsi"] for r in rows)
report={"period_start_inclusive":start,"period_end_exclusive":end,"samples":len(rows),"paired_rectangle_mmsi_sum":totold,"paired_marine_mmsi_sum":totnew,"summed_mmsi_difference_pct":round((totold-totnew)/totold*100,2) if totold else None,"note":"Summed per-sample MMSI are not unique vessels across the test period. Both methods use the same sample windows.","generated_at_utc":datetime.now(timezone.utc).isoformat()}
(out/"summary.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(report)
