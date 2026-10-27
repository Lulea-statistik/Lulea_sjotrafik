const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('docs/index.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
test('JavaScript parses',()=>{assert.ok(script);new Function(script)});
test('snapshot dates remain in native dropdown only',()=>{assert.match(html,/id="shipDay"/);assert.doesNotMatch(html,/shipShowAllDates/);assert.match(html,/opts\(selector,selector==='shipDay'\?\['ALL',\.\.\.paths\]:paths\)/);assert.match(html,/el\(selector\)\.value=paths\[0\]/)});
test('table scrolling and thirteen-row viewport',()=>{assert.match(html,/ship-table-scroll/);assert.match(html,/max-height:721px/);assert.match(html,/height:52px/)});
test('all eight columns sortable via keyboard and mouse',()=>{for(const key of ['flag','vessel','terminal','arrival','departure','status','route','purpose'])assert.match(html,new RegExp('data-ship-sort="'+key+'"'));assert.match(script,/function sortShipRows/);assert.match(script,/function chooseShipSort/);assert.match(script,/aria-sort/);assert.match(script,/keydown/)});
