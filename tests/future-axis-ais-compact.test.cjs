const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const html=fs.readFileSync('docs/index.html','utf8');
const js=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
test('inline JS parses',()=>{assert.ok(js);new Function(js)});
test('future months end rightmost with dynamic local month and right-aligned scroll',()=>{assert.match(js,/timeZone:'Europe\/Stockholm',year:'numeric',month:'2-digit'/);assert.match(js,/Array\.from\(\{length:24\}/);assert.match(js,/container\.scrollLeft=container\.scrollWidth-container\.clientWidth/)});
test('AIS hourly axis labels 01 to 24, 24 represents midnight',()=>{assert.match(js,/bins\.slice\(1\),bins\[0\]/);assert.match(js,/String\(b\.hour\|\|24\)\.padStart\(2,'0'\)/);assert.match(html,/24 avser kl\. 00/)});
test('AIS samples table is absent, latest sample summary kept',()=>{assert.doesNotMatch(html,/id="aisRows"/);assert.doesNotMatch(js,/fill\('aisRows'/);assert.match(html,/id="aisDetails"/)});
