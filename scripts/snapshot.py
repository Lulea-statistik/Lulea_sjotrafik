"""Archive the public Lulea port call listing; fail closed on markup changes."""
import hashlib, json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from bs4 import BeautifulSoup

URL="https://portlulea.com/sjotjanster/trafikinformation/"
ROOT=Path(__file__).resolve().parents[1]/"data"
FIELDS=("IMO-nummer","Ankommer från","Avgår till","Avsikt med besöket","Fartygstyp","Djupgående in","Djupgående ut","Flagg","Signal","Längd","Bredd","Bruttoton","DWT")

def extract(html):
    soup=BeautifulSoup(html,"html.parser")
    records=[]
    for tr in soup.select("tr"):
        text=tr.get_text("\n",strip=True)
        match=re.search(r"IMO-nummer:\s*(\d{7})",text)
        if not match: continue
        cells=[x.get_text(" ",strip=True) for x in tr.find_all("td",recursive=False)]
        fields={}
        for name in FIELDS:
            value=re.search(r"(?:^|\n)"+re.escape(name)+r":\s*([^\n]*)",text)
            fields[name]=value.group(1).strip() if value else None
        records.append({"imo":match.group(1),"columns":cells,"fields":fields,
                        "date_strings":re.findall(r"\d{2}/\d{2}/\d{2},?\s*\d{2}:\d{2}",text)})
    if not records: raise RuntimeError("No IMO rows parsed; refusing to archive potentially invalid page.")
    return records

def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    now=datetime.now(ZoneInfo("Europe/Stockholm"))
    today=now.date().isoformat()
    response=requests.get(URL,timeout=40,headers={"User-Agent":"Lulea-sjotrafik-history/1.0"})
    response.raise_for_status()
    response.encoding=response.apparent_encoding or "utf-8"
    html=response.text
    if "Fartyg i hamnen" not in html or "IMO-nummer" not in html:
        raise RuntimeError("Expected port listing missing")
    items=extract(html)
    payload={"date":today,"collected_at":now.isoformat(),"source":URL,"count":len(items),"records":items}
    save(ROOT/"snapshots"/(today+".json"),payload)
    raw=ROOT/"raw"/(today+".html")
    raw.parent.mkdir(parents=True,exist_ok=True)
    raw.write_text(html,encoding="utf-8")
    # Preserve daily snapshots as observations. Do not infer exact arrivals from disappearance.
    print(f"Archived {len(items)} public listing records for {today}")

if __name__=="__main__": main()
