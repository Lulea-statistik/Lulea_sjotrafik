const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const html=fs.readFileSync('docs/index.html','utf8');
const manifest=JSON.parse(fs.readFileSync('docs/data/manifest.json','utf8'));
const script=html.match(/<script>([\s\S]*?)<\/script>/)?.[1];
test('page javascript parses',()=>{assert.ok(script);new Function(script)});
test('all snapshot dates newest first',()=>{
 const fn=new Function(script+';return snapshotDates;')();
 for(const type of ['ships','cruises']){
  const values=manifest.datasets[type].map(x=>x.path);
  const result=fn(values);
  assert.equal(result.length,new Set(values).size);
  assert.deepEqual(result,[...result].sort((a,b)=>b.localeCompare(a)));
 }
});
test('AIS axis has explicit date labels',()=>{assert.match(script,/const xLabels=/);assert.match(script,/Datum \(MM-DD\)/)});
test('snapshot initial selection newest available',()=>{assert.match(script,/el\(selector\)\.value=paths\[0\]/)});
