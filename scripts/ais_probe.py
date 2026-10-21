"""AISStream 90-second samples filtered to Lulea's NMD marine-water polygon.

AISStream supports only bounding-box subscriptions. Each received position is checked
against the marine polygon before counting. Older samples remain unfiltered.
"""
import asyncio
import json
import math
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import requests
import websockets
from shapely.geometry import Point, shape
from shapely.ops import unary_union
from shapely import transform
from pyproj import Transformer

API = "wss://stream.aisstream.io/v0/stream"
GEO_URL = ("https://raw.githubusercontent.com/Lulea-statistik/"
           "SMHI_Lulea-Kallax_weather-climate/main/data/lightning/geography_nmd.geojson")
OUT = Path(__file__).resolve().parents[1] / "data" / "ais_probe"


def load_marine_polygon():
    response = requests.get(GEO_URL, timeout=90)
    response.raise_for_status()
    features = response.json().get("features", [])
    marine = [shape(f["geometry"]) for f in features
              if (f.get("properties") or {}).get("class") == "sea"]
    if not marine:
        raise RuntimeError("No marine-water feature in NMD GeoJSON; refusing unfiltered count")
    region = unary_union(marine)
    if not region.is_valid:
        raise RuntimeError("Invalid NMD marine polygon; refusing to count")
    min_lon, min_lat, max_lon, max_lat = region.bounds
    if region.area < 0.01 or max_lon - min_lon < 0.2 or max_lat - min_lat < 0.1:
        raise RuntimeError("NMD sea polygon is implausibly small; refusing to count")
    # GeoJSON WGS84 (EPSG:4326): longitude/latitude.
    box = [[min_lat, min_lon], [max_lat, max_lon]]
    return region, box


def position(message):
    typ = message.get("MessageType")
    body = (message.get("Message") or {}).get(typ) or {}
    lat, lon = body.get("Latitude"), body.get("Longitude")
    if lat is None or lon is None:
        return None
    try:
        lat, lon = float(lat), float(lon)
    except (ValueError, TypeError):
        return None
    if not math.isfinite(lat) or not math.isfinite(lon) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return Point(lon, lat)


async def main():
    key = os.getenv("AISSTREAM_API_KEY")
    if not key:
        raise RuntimeError("AISSTREAM_API_KEY missing")
    sea, box = load_marine_polygon()
    seen = Counter()
    mmsi = set()
    position_quality = {}
    to_metric = Transformer.from_crs("EPSG:4326", "EPSG:3006", always_xy=True)
    sea_metric = transform(sea, to_metric.transform, interleaved=False)
    sea_edge = sea_metric.boundary
    rejected = Counter()
    started = datetime.now(timezone.utc)
    async with websockets.connect(API, open_timeout=20, ping_interval=20, compression="deflate") as ws:
        await ws.send(json.dumps({"APIKey": key, "BoundingBoxes": [box],
            "FilterMessageTypes": ["PositionReport", "StandardClassBPositionReport"]}))
        loop = asyncio.get_running_loop()
        stop = loop.time() + 90
        while loop.time() < stop:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=min(10, max(0.1, stop-loop.time())))
            except asyncio.TimeoutError:
                continue
            item = json.loads(msg)
            p = position(item)
            if p is None:
                rejected["missing_position"] += 1
                continue
            is_inside = sea.covers(p)
            metric_point = transform(p, to_metric.transform, interleaved=False)
            is_boundary = metric_point.distance(sea_edge) <= 30
            if not is_inside:
                rejected["outside_marine_polygon"] += 1
                if is_boundary:
                    rejected["outside_within_30m"] += 1
                continue
            typ = item.get("MessageType", "unknown")
            seen[typ] += 1
            meta = item.get("MetaData") or {}
            if meta.get("MMSI"):
                ident = str(meta["MMSI"])
                mmsi.add(ident)
                quality = "uncertain_boundary" if is_boundary else "safe_marine"
                if ident not in position_quality or quality == "safe_marine":
                    position_quality[ident] = quality
    day = started.date().isoformat()
    stamp = started.strftime("%Y-%m-%dT%H-%M-%SZ")
    result = {
        "sample_started_utc": started.isoformat(),
        "sample_seconds": 90,
        "sampling_hour_utc": started.hour,
        "bbox_wgs84_latlon": box,
        "geographic_filter": "lulea_nmd_marine_v1",
        "geographic_filter_source": GEO_URL,
        "message_counts": dict(seen),
        "unique_mmsi_count": len(mmsi),
        "rejected_message_counts": dict(rejected),
        "quality_margin_m": 30,
        "quality_classification_crs": "EPSG:3006",
        "quality_unique_mmsi": dict(Counter(position_quality.values())),
        "quality_summary": ("uncertain_boundary" if "uncertain_boundary" in position_quality.values()
                            else "safe_marine" if mmsi
                            else "outside_marine" if rejected["outside_marine_polygon"] else "no_positions"),
        "warning": "Only received positions within NMD marine water; not continuous vessel coverage"
    }
    (OUT/day).mkdir(parents=True, exist_ok=True)
    (OUT/day/(stamp + ".json")).write_text(json.dumps(result, indent=2) + "\n")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
