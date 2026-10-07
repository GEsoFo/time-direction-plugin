// Reuse the project's pure paipan engine, driven by the calendar's fixed facts.
import {paiPanCore, ZHI, TIAN_JIANG, SHEN_NAMES} from '../assets/liuren-core.mjs';
process.stdin.setEncoding('utf8');
let input='';for await(const chunk of process.stdin)input+=chunk;
const items=JSON.parse(input),charts={};
for(const [key,f] of Object.entries(items)){
 const gz=p=>({gan:p[0],zhi:p[1]});
 const r=paiPanCore({day:gz(f.day),hour:gz(f.hour),yueJiang:f.jiang,shiZhi:f.hour[1]});
 for(let i=0;i<12;i++)if(r.tianPan[i]!==f.sky[ZHI[i]])throw Error('Plate differs: '+key);
 // Core transmissions do not depend on the noble table. Align ALL heavenly
 // generals and nested shen records to the selected calendar noble/daylight.
 const ground=ZHI.indexOf(f.noble.ground),gui=ZHI.indexOf(f.noble.branch);
 const forward=ground===11||ground<=4;
 const general=zhi=>TIAN_JIANG[((forward?ZHI.indexOf(zhi)-gui:gui-ZHI.indexOf(zhi))+12)%12];
 const update=s=>({...s,tianJiang:general(s.zhi)});
 r.wei=r.wei.map(w=>({...w,shen:update(w.shen)}));
 r.siKe=r.siKe.map(k=>({...k,upInfo:update(k.upInfo)}));
 r.sanChuan={...r.sanChuan,chu:update(r.sanChuan.chu),zhong:update(r.sanChuan.zhong),mo:update(r.sanChuan.mo)};
 charts[key]={dayNight:f.noble.phase==='昼贵'?'昼':'夜',guiRen:f.noble.branch,guiRenName:SHEN_NAMES[f.noble.branch],
   guiRenShunNi:forward?'顺':'逆',wei:r.wei,siKe:r.siKe,sanChuan:r.sanChuan,
   xunKong:r.xunKong,xunShou:r.xunShou,shenSha:r.shenSha};
}
process.stdout.write(JSON.stringify(charts));
