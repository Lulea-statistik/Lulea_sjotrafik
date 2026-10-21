#!/usr/bin/env python3
"""Daily source check for published cruise passenger capacities.

Conservative: scrape public specification text once daily; do not replace
verified capacity automatically when a site's markup or number changes.
"""
import datetime,json,re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"data/cruise/passenger_capacity.json"
data=json.loads(p.read_text(encoding="utf-8"))
session=requests.Session()
session.headers["User-Agent"]="Lulea-statistik/1.0 (public vessel-specifications check; daily)"
for ship in data["vessels"]:
    try:
        response=session.get(ship["source"],timeout=25)
        response.raise_for_status()
        text=BeautifulSoup(response.text,"html.parser").get_text(" ",strip=True)
        expected=str(ship["normal_passengers"])
        # Never silently rewrite disputed facts.
        ship["source_check"]="pass" if re.search(r"(?<!\\d)"+expected+r"(?!\\d)",text) else "manual_review"
    except requests.RequestException:
        ship["source_check"]="unavailable"
    ship["source_checked_at"]=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
data["updated_at"]=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print([(s["vessel"],s["source_check"]) for s in data["vessels"]])
