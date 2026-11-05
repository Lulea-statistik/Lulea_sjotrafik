# AIS-metodbrott och parallelljämförelse, 22 oktober–4 november 2026

## Beslut för historiska tidsserier

**Bevara historiska råvärden utan justering och särredovisa serierna efter metod.** Använd inte en generell omräkningsfaktor. Markera metodbrott i alla långtidsdiagram och ange filtreringsmetod i datatabeller, export och diagramförklaring.

* Före metodbytet: historisk rektangelbaserad AIS-statistik (äldre geografisk utbredning).
* Efter metodbytet: NMD-havsvattenfiltrerad AIS-statistik.
* Parallellproven: kvalitetsunderlag; summera inte per-prov-unika MMSI som unika fartyg över hela perioden.

## Verifierat från parade data

Källor: `data/ais_method_comparison/paired_samples.csv`, `data/ais_method_comparison/summary.json` och `scripts/ais_probe.py`.

* Tidsintervall: 2026-10-22 till och med 2026-11-04 (UTC).
* 61 jämförbara parallellprov, 90 sekunder vardera.
* Summerade provvisa MMSI: rektangel 171, NMD 139; minskning 32 eller 18,71 % av rektangelsumman.
* Positionsmeddelanden: rektangel 185, NMD 151; minskning 34 eller 18,38 %.
* Median provvis absolut MMSI-differens: 0. Median procentuell differens bland prov med rektangel-MMSI > 0: 0 %.
* Fördelning MMSI-differens: 34 prov med 0, 23 med 1, 3 med 2, 1 med 3.
* 4 prov med 0 MMSI i båda metoderna; dessa är nollobservationer, inte bortfall.
* 4 prov med MMSI i rektangel men inga i NMD. Maximal absolut avvikelse 3 MMSI (2026-10-26 12:53 UTC). Procentuell minskning 100 % förekommer i prov med få observationer.

**Varning om bortfall:** Andelen genomförda stickprov relativt avsett schema kan inte fastställas säkert ur dessa två filer ensamma. Inventera GitHub Actions och separata provfiler innan planerat kontra faktiskt antal beskrivs som ett driftbortfall. Kontrollera även eventuella stickprov som inte har båda metodernas fält.

## Varför historiken inte ska korrigeras med 18,71 %

Den parade jämförelsen använder **samma** AISStream-bounding-box, med respektive utan NMD-mask på positionerna. Tidigare historiska rektangelprov kan ha haft **en annan bounding-box**. Därför isolerar det parade testet NMD-filtreringens effekt inom den nya rektangeln, men mäter inte hela skillnaden mellan de äldre historiska och nya geografiska definitionerna. Provens beläggning varierar dessutom kraftigt.

En viktad differens på 18,71 % är därmed inte en legitim korrigeringsfaktor för den äldre serien. Äldre aggregerade observationer kan inte reprojiceras eller NMD-filtreras i efterhand utan ursprungliga koordinater.

## Kvalitetskontroll av NMD-gränsen, 30 meter

I `scripts/ais_probe.py` hämtas geometri via en GeoJSON-källa (angiven som EPSG:4326). Geometri och punkter transformeras till **EPSG:3006** för avstånd i meter. NMD accepterar positioner med `sea.covers(p)`, och kvalitetsmarginalen är för närvarande **30 m** till vattenpolygonens gräns.

**Hypotes att testa, inte fastslaget resultat:** en del rektangelöverskott kan bero på kustnära lägesosäkerhet, hamnbassängers geometri eller verkliga positioner på land. Både GPS-fel och geometriors aktualitet kan påverka tolkningen. 30-metersmarginalen är en klassificeringsgräns, inte en verifierad AIS-noggrannhet.

### Nästa mätning

1. Spara per prov aggregat över bortfiltrerade positionsmeddelanden uppdelat i `outside_within_30m` och `outside_beyond_30m`, samt meddelanden som accepterats inom 30 m från gränsen. Spara även antal **unika MMSI** per kategori utan att dubbelräkna fartyg mellan kategorier.
2. För en geografisk kontroll av enstaka avvikare: spara begränsade, pseudonymiserade kvalitetsuppgifter eller aggregerade rutnätsantal enligt tillämpliga dataskydds- och åtkomstkrav; spara inte identifierbara AIS-spår slentrianmässigt i det publika repot.
3. Verifiera NMD-filens CRS, version och geografisk täckning samt att `EPSG:3006` ger rimliga avstånd för området. Dokumentera maskans datum och källversion.
4. Jämför alternativt känslighetsutfall vid 0, 10, 30 och 50 m som **diagnostik**. Ändra inte produktionsfiltreringen baserat på enbart en sådan känslighetsanalys.
5. Kontrollera varför prov saknas i paret eller varför planerade tidsfönster inte kördes: schemaläggning, nyckel-/nätfel, avbrott eller ofullständig arkivering.

## Rekommenderad publicering

* Lägg ett synligt vertikalt metodstreck vid verifierad övergångstid i samtliga AIS-tidsdiagram.
* Ge användaren metodetikett, källversion, provlängd och antal genomförda prov vid hover/export.
* Visa inte en okommenterad sammanhängande trend över metodgränsen; särredovisa eller gråmarkera jämförelsen.
* Publicera gärna den parade provjämförelsen som separat kvalitetsdiagram: MMSI-rektangel och MMSI-NMD per identiskt stickprov, samt provdifferens.
* Revidera detta beslut först om nya, **positionsbaserade** återberäkningar kan skapa jämförbara historiska områden.

## Automatisk uppföljning

Kör `python scripts/audit_ais_method_comparison.py` för att reproducera nyckeltal och identifiera extremprov, nollprov och saknade kalenderdagar i de parade provfilerna. Scriptet ändrar inga rådata.
