const test=require('node:test');
const assert=require('node:assert/strict');
const {hourly}=require('../docs/ais-hourly-average.js');
test('averages all samples in the same local hour',()=>{
 const items=[{sample_started_utc:'2026-10-26T10:00:00Z',message_counts:{PositionReport:8,StandardClassBPositionReport:2}},{sample_started_utc:'2026-10-26T10:30:00Z',message_counts:{PositionReport:6}}];
 const h=hourly(items);assert.equal(h[11].mean,8);assert.equal(h[11].samples,2);
});
test('absence is null not zero',()=>{const h=hourly([]);assert.equal(h[0].mean,null);assert.equal(h[0].samples,0)});
test('daylight saving fall back uses local hour',()=>{
 const h=hourly([{sample_started_utc:'2026-10-25T00:30:00Z',message_counts:{PositionReport:4}},{sample_started_utc:'2026-10-25T01:30:00Z',message_counts:{PositionReport:8}}]);
 assert.equal(h[2].samples,2);assert.equal(h[2].mean,6);
});
