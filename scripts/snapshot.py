"""Daily public port-call and cruise schedule snapshots."""
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]/"data"
URLS={"commercial":"https://portlulea.com/sjotjanster/trafikinformation/",
      "cruise":"https://portlulea.com/sjotjanster/kryssningsfartyg/"}

def clean(x):
    return " ".join(x.get_text(" ",strip=True).split())

def extract_commercial(soup):
    records=[]
    for row in soup.select("tr.c-ahoy-port-list__row"):
        detail=row.find_next_sibling("tr")
        if not detail or "c-ahoy-port-list__row-content" not in detail.get("class",[]): continue
        fields={}
        for tr in detail.select("tr"):
            th=tr.find("th")
            td=tr.find("td")
            if th and td: fields[clean(th).rstrip(":")]=clean(td)
        imo=fields.get("IMO-nummer")
        if not imo: continue
        datecell=row.select_one(".c-ahoy-port-list-date .d-none.d-md-block")
        dates=list(datecell.stripped_strings) if datecell else []
        records.append({
          "source_type":"commercial",
          "vessel":clean(row.select_one(".c-ahoy-port-vessel")) if row.select_one(".c-ahoy-port-vessel") else "",
          "imo":imo,"arrival":dates[0] if len(dates)>0 else None,
          "departure":dates[1] if len(dates)>1 else None,
          "terminal":clean(row.select_one(".c-ahoy-port-list-terminal")) if row.select_one(".c-ahoy-port-list-terminal") else "",
          "agent":clean(row.select_one(".c-ahoy-port-list-agent")) if row.select_one(".c-ahoy-port-list-agent") else "",
          "status":clean(row.select_one(".c-ahoy-port-list-status")) if row.select_one(".c-ahoy-port-list-status") else "",
          "details":fields
        })
    if not records: raise RuntimeError("No commercial port rows found; source may have changed")
    return records

def extract_cruise(soup):
    table=None
    for candidate in soup.select("table"):
        headings=[clean(th).casefold() for th in candidate.select("thead th")]
        if not headings:
            first=candidate.find("tr")
            headings=[clean(th).casefold() for th in first.find_all(["th","td"])] if first else []
        if "ankommer" in headings and "fartyg" in headings and "terminal" in headings:
            table=candidate
            break
    if table is None: raise RuntimeError("Cruise arrival table not found; refusing empty data")
    rows=table.select("tbody tr") or table.select("tr")[1:]
    result=[]
    for row in rows:
        cells=[clean(cell) for cell in row.find_all("td",recursive=False)]
        if len(cells)<4: continue
        result.append({"source_type":"cruise","planned_arrival":cells[0],
          "planned_departure":cells[1],"vessel":cells[2],"terminal":cells[3],
          "origin":cells[4] if len(cells)>4 else None,
          "destination":cells[5] if len(cells)>5 else None,
          "status":"planned"})
    # An empty but well-formed table is valid: no currently scheduled cruise calls.
    return result

def save(path,contents):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(contents,encoding="utf-8")

def main():
    now=datetime.now(ZoneInfo("Europe/Stockholm"))
    day=now.date().isoformat()
    # Fetch and validate both before writing: a malformed source fails the entire run.
    staged={}
    for category,url in URLS.items():
        r=requests.get(url,timeout=40,headers={"User-Agent":"Lulea-sjotrafik-history/1.1"})
        r.raise_for_status()
        r.encoding=r.apparent_encoding or "utf-8"
        soup=BeautifulSoup(r.text,"html.parser")
        records=extract_commercial(soup) if category=="commercial" else extract_cruise(soup)
        staged[category]=(r.text,records,url)
    for category,(html,records,url) in staged.items():
        prefix="cruise" if category=="cruise" else ""
        raw=ROOT/("cruise/raw" if prefix else "raw")/(day+".html")
        structured=ROOT/("cruise/snapshots" if prefix else "snapshots")/(day+".json")
        save(raw,html)
        save(structured,json.dumps({"date":day,"collected_at":now.isoformat(),"source":url,
             "count":len(records),"records":records},ensure_ascii=False,indent=2)+"\n")
        print(category,day,len(records))

if __name__=="__main__": main()
