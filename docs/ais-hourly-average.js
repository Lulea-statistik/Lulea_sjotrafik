/* Mean AIS position reports per sampled local clock hour. */
(function(root){
 function hourly(samples){
  const bins=Array.from({length:24},(_,hour)=>({hour,count:0,total:0}));
  const fmt=new Intl.DateTimeFormat('sv-SE',{timeZone:'Europe/Stockholm',hour:'2-digit',hourCycle:'h23'});
  for(const sample of samples){
   if(!sample.sample_started_utc)continue;
   const date=new Date(sample.sample_started_utc);
   if(Number.isNaN(date.getTime()))continue;
   const hour=Number(fmt.format(date));
   const counts=sample.message_counts||{};
   const total=Number(counts.PositionReport||0)+Number(counts.StandardClassBPositionReport||0);
   if(!Number.isInteger(hour)||hour<0||hour>23||!Number.isFinite(total))continue;
   bins[hour].count++;bins[hour].total+=total;
  }
  return bins.map(b=>({hour:b.hour,label:String(b.hour).padStart(2,'0')+':00',
    mean:b.count?b.total/b.count:null,samples:b.count}));
 }
 const api={hourly};
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 root.AisHourlyAverage=api;
})(typeof globalThis!=='undefined'?globalThis:this);
