# Luleå sjötrafik – historik och AIS-pilot

Datakällor:
- [Luleå Hamns trafikinformation](https://portlulea.com/sjotjanster/trafikinformation/) – dagliga snapshots.
- [AISStream](https://aisstream.io/documentation/) – valfri, manuell täckningskontroll (inte komplett AIS-historik).

## Kryssningsfartyg
Kryssningsanlöp hämtas varje dag från [hamnens kryssningssida](https://portlulea.com/sjotjanster/kryssningsfartyg/) och lagras separat i `data/cruise/raw/YYYY-MM-DD.html` och `data/cruise/snapshots/YYYY-MM-DD.json`. Uppgifterna är **planerade anlöp**, inte bekräftat genomförda besök. Återkommande fartyg med olika planerade besöksdatum är separata poster. Genom att bevara dagskopior kan ombokningar och inställda besök analyseras senare. Alla kommersiella hamnanlöp lagras separat. Dubbelräkning mellan de två källorna måste hanteras före eventuell sammanlagd statistik.

## Status
GitHub Actions-arbetsflöden och insamlingsskript är installerade. **Den första framgångsrika körningen är ännu inte verifierad.** Därför ska datainsamlingen inte betraktas som aktiv och kvalitetssäkrad förrän en körning gett giltiga datafiler.

- **Actions > Daily port snapshot > Run workflow:** hämtar både hamnens vanliga anlöpstabell och kryssningsplaneringen och arkiverar HTML och JSON i `data/raw/` och `data/snapshots/`. Schemalagd dagligen 05:17 UTC (07:17 svensk sommartid och 06:17 vintertid).
- **Actions > AIS coverage pilot > Run workflow:** kräver en hemlig nyckel `AISSTREAM_API_KEY` under repo Settings > Secrets and variables > Actions. Samlar endast ett 90-sekunders aggregat av mottagna AIS-meddelanden, inte individuella positioner.
- Läs [datamodell och begränsningar](docs/DATA_MODEL.md).

## Metod och reservationer
Dagliga snapshots av ett rullande, delvis prognostiserat hamnschema kan **inte** likställas med officiellt bekräftade anlöp. Historiska besök måste dedupliceras med IMO, terminal och besökstid. En förändring eller ett försvinnande från listan är inte bevis för faktisk avgång. Kortvariga besök kan saknas helt. Den första lyckade körningens parserresultat måste kvalitetsgranskas mot webbplatsens tabell.

AIS-pilotens täckning, kommersiella villkor och rätt till vidarepublicering behöver verifieras innan positionsloggning i skarpt läge. Pilotens koordinatrektangel anges som latitud/longitud i EPSG:4326 och är inte någon officiell hamngräns.

Källa: Luleå Hamn. Råhistorik och AIS-information bör inte vidarepubliceras innan datakällornas återanvändningsvillkor är kontrollerade.
