const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('docs/index.html','utf8');
const manifest=JSON.parse(fs.readFileSync('docs/data/manifest.json','utf8'));
test('page JavaScript parses',()=>{
 const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
 assert.ok(script);new Function(script);
});
test('all ship dates remain selectable newest first',()=>{
 const ships=manifest.datasets.ships;
 assert.ok(ships.length>1);
 assert.match(html,/const paths=snapshotDates\(await list\(folder\)\)/);
 assert.match(html,/el\(selector\)\.value=paths\[0\]/);
 assert.match(html,/shipDayCount/);
});
test('AIS chart shows number of samples by clock hour',()=>{
 assert.match(html,/class="ais-sample-count"/);
 assert.match(html,/b\.samples\?b\.samples/);
 assert.match(html,/AisHourlyAverage\.hourly\(ais\)/);
});
