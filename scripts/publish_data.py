#!/usr/bin/env python3
"""Publish selected archived JSON snapshots as static GitHub Pages assets."""
from pathlib import Path
import json
import shutil
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
target = root / "docs" / "data"
folders = {
    "ships": "data/snapshots",
    "cruises": "data/cruise/snapshots",
    "ais": "data/ais_probe",
}
manifest = {"generated_at_utc": datetime.now(timezone.utc).isoformat(), "datasets": {}}
for name, folder in folders.items():
    source = root / folder
    files = sorted(source.rglob("*.json"), reverse=True) if source.exists() else []
    published = []
    for file in files[:120]:
        relative = file.relative_to(root)
        output = root / "docs" / relative
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError):
            continue
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(file, output)
        published.append({"path": str(relative).replace("\\", "/"), "date": data.get("date") or data.get("sample_started_utc"), "count": data.get("count", len(data.get("records", [])) if isinstance(data.get("records"), list) else None)})
    manifest["datasets"][name] = published
target.mkdir(parents=True, exist_ok=True)
(target / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
