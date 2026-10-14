"""Optional AISStream observation probe. Requires AISSTREAM_API_KEY in secrets.

Runs for at most 90 seconds per invocation. This is a SAMPLE, not full-day coverage.
Raw AIS messages are not committed; only a small summary is stored until licensing
and coverage have been verified.
"""
import asyncio, json, os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import websockets

BOX=[[65.35,21.40],[65.85,23.00]]  # WGS84 lat/lon; deliberately broad pilot region
API="wss://stream.aisstream.io/v0/stream"
OUT=Path(__file__).resolve().parents[1]/"data"/"ais_probe"

async def main():
    key=os.getenv("AISSTREAM_API_KEY")
    if not key:
        raise RuntimeError("AISSTREAM_API_KEY missing. Add it in repository Actions secrets before running.")
    seen=Counter()
    mmsi=set()
    started=datetime.now(timezone.utc)
    async with websockets.connect(API,open_timeout=20,ping_interval=20,compression="deflate") as ws:
        await ws.send(json.dumps({"APIKey":key,"BoundingBoxes":[BOX],
            "FilterMessageTypes":["PositionReport","StandardClassBPositionReport"]}))
        loop=asyncio.get_running_loop()
        stop=loop.time()+90
        while loop.time()<stop:
            try: msg=await asyncio.wait_for(ws.recv(),timeout=min(10,max(0.1,stop-loop.time())))
            except asyncio.TimeoutError: continue
            item=json.loads(msg)
            typ=item.get("MessageType","unknown")
            seen[typ]+=1
            meta=item.get("MetaData") or {}
            if meta.get("MMSI"): mmsi.add(str(meta["MMSI"]))
    day=started.date().isoformat()
    result={"sample_started_utc":started.isoformat(),"sample_seconds":90,
       "bbox_wgs84_latlon":BOX,"message_counts":dict(seen),
       "unique_mmsi_count":len(mmsi),"warning":"Sample coverage only; not continuous AIS history"}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/(day+".json")).write_text(json.dumps(result,indent=2)+"\n")
    print(result)

if __name__=="__main__": asyncio.run(main())
