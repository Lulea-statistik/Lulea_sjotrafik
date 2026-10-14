# Data model and limitations

## Sources
1. Port of Lulea public rolling call listing: daily HTML and parsed JSON snapshots.
2. AISStream (optional pilot): short coverage samples with aggregated counts only.

## Files
- `data/raw/YYYY-MM-DD.html`: immutable-by-day page source; reruns replace same day's file.
- `data/snapshots/YYYY-MM-DD.json`: structured source observations; no inferred visits.
- `data/ais_probe/YYYY-MM-DD.json`: sample message counts without positions.

## Quality rules
- If a listing cannot be parsed, the workflow fails, not zero ship calls.
- A missing vessel in a later rolling listing is **not** a confirmed departure.
- IMO identifies a vessel, not a visit. Separate calls need stable composite identifiers
  based on IMO, berth/terminal and a verified arrival time window.
- AIS uses MMSI; link to IMO only using separately verified vessel metadata.
- The sample bounding rectangle is WGS84 (EPSG:4326) and is **not** an official
  harbor or municipality boundary.
- AIS probe is voluntary/manual only until coverage, accuracy and redistribution rights
  are confirmed. Do not publish raw AIS feeds without permission.
- GitHub Actions cron is approximate; runs can be delayed or skipped.
- One daily snapshot may miss short stays, and the listing includes preliminary events.

## AIS automatic pilot schedule (2026-10-14)
- 90-second samples every hour at 06:13–17:13 UTC; additional samples at 00:13, 03:13, 18:13 and 21:13 UTC, 16 runs per day.
- UTC times are fixed: in Swedish winter local time is UTC+1, in summer UTC+2. This prioritizes daytime but does **not** track actual sunrise or sunset; Lulea experiences large seasonal daylight variation.
- Every successful sample uses its own timestamped file under `data/ais_probe/YYYY-MM-DD/` to prevent same-day overwrite.
- Each sample stores only aggregated message counts and distinct MMSI count; no positions or individual MMSIs are stored.
- Scheduled runs can be delayed or omitted by GitHub. The output is **sampling coverage**, not continuous vessel movement history.
- Only expand to position history after coverage checks, source terms and any redistribution rights have been confirmed.
