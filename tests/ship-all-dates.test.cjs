const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const html=fs.readFileSync('docs/index.html','utf8'),js=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
test('page script parses',()=>{assert.ok(js);new Function(js)});
test('all dates option is in dropdown, defaults to latest day',()=>{assert.match(js,/\['ALL',\.\.\.paths\]/);assert.match(js,/Alla datum – sammanställd lista/);assert.match(js,/el\(selector\)\.value=paths\[0\]/);assert.doesNotMatch(html,/shipShowAllDates/)});
test('aggregate loads all saved day snapshots and shows source day',()=>{assert.match(js,/Promise\.allSettled\(shipSnapshotPaths\.map/);assert.match(js,/snapshot_date/);assert.match(js,/selectShipSnapshot/);assert.match(js,/samma fartyg kan förekomma flera/);});
