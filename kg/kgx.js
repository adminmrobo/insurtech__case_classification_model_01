/* ai-lab-retrofit 휴대판 (색 변수가 없는 페이지에서도 동작) */
/* ══ KG: 지식 색인(#kg) + 온톨로지·서지 꾸러미(#export) — 공용 모듈 ══
   데이터 블록: #kg-raw(중립 JSON), #refs-csl(CSL-JSON), #page-meta, #kg-ld(빌드 때 생성)
   외부 라이브러리 없음. 모든 내보내기는 kg-raw에서 만든다. */
var KGX=(function(){
'use strict';
function $id(i){return document.getElementById(i);}
function J(id){var e=$id(id); return e?JSON.parse(e.textContent):null;}
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function el(tag,cls,html){var e=document.createElement(tag); if(cls)e.className=cls; if(html!=null)e.innerHTML=html; return e;}

var TYPE={Concept:['개념','#82b8ff'],Method:['방법','#5ee39c'],BioAnalogue:['생물 대응','#ef5b5b'],Claim:['주장','#f1b646'],
  Question:['열린 질문','#d672d6'],Limitation:['한계','#ff9a7a'],Task:['과제','#7fe0c8'],Metric:['지표','#b9a8ff'],
  Dataset:['데이터','#c9c4a4'],Simulation:['시뮬레이션','#8a88a8'],QuizItem:['퀴즈','#9a90c4'],Work:['문헌','#e0d7a8'],
  Area:['영역','#eceaf3'],Topic:['주제','#9d9bb8'],Analogy:['비유','#ff86b8'],Term:['용어','#82b8ff'],
  Theory:['이론·모형','#9ab0d0'],Assumption:['가정','#c9b8ff'],Identity:['항등식','#b8a27a'],Standard:['기준·법령','#d9a066'],
  Account:['계정과목','#b8a27a'],Indicator:['공식 지표','#7fd1a8'],Distribution:['확률분포','#9ab0d0'],Framework:['분석 틀','#d98c6a'],
  Definition:['정의','#a8c8f0'],Theorem:['정리','#f0a8c8'],Axiom:['공리','#e0c070'],Proof:['증명','#c0a0e0'],Structure:['수학적 대상','#90d0c0'],Estimator:['추정량','#b0d890']};
var REL={prerequisiteOf:'먼저 알아야 함',hasLimitation:'한계',addressedBy:'해결됨',partOf:'부분',bioAnalogueOf:'생물 대응',
  contrastsWith:'대비',supports:'뒷받침',assertedIn:'출처',evaluatedBy:'지표로 평가',evaluatedOn:'데이터로 평가',
  demonstratedBy:'시뮬레이션',raises:'질문을 낳음',relatedTo:'관련',solves:'해결 과제',analogyOf:'비유',assesses:'퀴즈 확인',
  broader:'상위 주제',explainedIn:'설명 위치',inspiredBy:'착상',assumes:'가정',derivedFrom:'유도됨',governedBy:'기준',
  supersededBy:'개정으로 대체',measuredBy:'지표로 잼',appliesIn:'적용 관할',
  implies:'함의',specialCaseOf:'특수한 경우',equivalentTo:'같음',provedBy:'증명',instanceOf:'예',counterexampleTo:'반례'};
function tl(t){return (TYPE[t]||[t])[0];} function tc(t){return (TYPE[t]||[0,'#9d9bb8'])[1];}
function pn(p){return p.replace(/^lab:/,'');}
function lab(n){return n.label?(n.label.ko||n.label.en):n.id;}

/* ── 변환기 ─────────────────────────────────────────── */
var NS='urn:lab:';
var CTX={'@vocab':NS,lab:NS,skos:'http://www.w3.org/2004/02/skos/core#',schema:'https://schema.org/',
  dct:'http://purl.org/dc/terms/',prov:'http://www.w3.org/ns/prov#',rdfs:'http://www.w3.org/2000/01/rdf-schema#'};
var SKOS_T={Concept:1,Method:1,Task:1,Term:1,Limitation:1,BioAnalogue:1,Metric:1,Area:1,Topic:1,Theory:1,Assumption:1,Identity:1,Account:1,Distribution:1,Framework:1,Definition:1,Theorem:1,Axiom:1,Structure:1,Estimator:1};
var SCH_T={Work:'schema:ScholarlyArticle',Claim:'schema:Claim',Dataset:'schema:Dataset',QuizItem:'schema:Question',Question:'schema:Question',Simulation:'schema:SoftwareApplication',Standard:'schema:Legislation',Indicator:'schema:StatisticalVariable'};
function lit(o){var a=[]; Object.keys(o||{}).forEach(function(k){ var v=o[k]; (Array.isArray(v)?v:[v]).forEach(function(x){a.push({'@value':x,'@language':k});});}); return a;}
function toJsonLd(g,meta){
  var graph=g.nodes.map(function(n){
    var t=['lab:'+n.type]; if(SKOS_T[n.type])t.push('skos:Concept'); if(SCH_T[n.type])t.push(SCH_T[n.type]);
    var o={'@id':n.id,'@type':t,'skos:prefLabel':lit(n.label)};
    if(n.altLabel)o['skos:altLabel']=lit(n.altLabel);
    if(n.definition)o['skos:definition']=lit(n.definition);
    ['level','status','confidence','coverage','family','page','anchor'].forEach(function(k){ if(n[k]!=null)o['lab:'+k]=n[k];});
    (n.match||[]).forEach(function(m){ var p=m.rel==='exact'?'skos:exactMatch':'skos:closeMatch'; (o[p]=o[p]||[]).push({'@id':m.iri});});
    return o;});
  var byS={}; graph.forEach(function(o){byS[o['@id']]=o;});
  g.edges.forEach(function(e){ var s=byS[e.s]; if(!s)return; var k=e.p; (s[k]=s[k]||[]).push({'@id':e.o});
    if(e.p==='lab:broader')(s['skos:broader']=s['skos:broader']||[]).push({'@id':e.o});
    if(e.p==='lab:assertedIn')(s['prov:wasDerivedFrom']=s['prov:wasDerivedFrom']||[]).push({'@id':e.o});
    if(e.p==='lab:relatedTo')(s['skos:related']=s['skos:related']||[]).push({'@id':e.o});
    if(e.p==='lab:specialCaseOf')(s['skos:broader']=s['skos:broader']||[]).push({'@id':e.o});
    if(e.p==='lab:equivalentTo')(s['skos:exactMatch']=s['skos:exactMatch']||[]).push({'@id':e.o}); });
  if(meta)graph.unshift({'@id':NS+'page/'+meta.number,'@type':['schema:LearningResource','schema:WebPage'],'schema:name':meta.title,
    'schema:inLanguage':meta.language,'schema:dateCreated':meta.date,'schema:version':meta.version,'dct:isPartOf':meta.series,
    'schema:about':(meta.about||[]).map(function(a){return {'@id':a};}),'schema:educationalLevel':meta.educationalLevel,
    'schema:learningResourceType':meta.learningResourceType,'dct:source':(meta.basedOn||[]).map(function(b){return {'@id':'lab:work/'+b};})});
  return {'@context':CTX,'@graph':graph};
}
function ttlS(s){return '"'+String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"').replace(/\n/g,'\\n')+'"';}
function ttlI(id){return id.indexOf('lab:')===0?'lab:'+id.slice(4).replace(/[^A-Za-z0-9_\-]/g,function(c){return c==='/'?'_':encodeURIComponent(c).replace(/%/g,'_');}):'<'+id+'>';}
function toTurtle(g){
  var L=['@prefix lab: <'+NS+'> .','@prefix skos: <http://www.w3.org/2004/02/skos/core#> .','@prefix schema: <https://schema.org/> .',
    '@prefix prov: <http://www.w3.org/ns/prov#> .',''];
  var out={}; g.edges.forEach(function(e){(out[e.s]=out[e.s]||[]).push(e);});
  g.nodes.forEach(function(n){
    var P=['a lab:'+n.type+(SKOS_T[n.type]?', skos:Concept':'')];
    Object.keys(n.label||{}).forEach(function(k){P.push('skos:prefLabel '+ttlS(n.label[k])+'@'+k);});
    Object.keys(n.altLabel||{}).forEach(function(k){[].concat(n.altLabel[k]).forEach(function(v){P.push('skos:altLabel '+ttlS(v)+'@'+k);});});
    Object.keys(n.definition||{}).forEach(function(k){P.push('skos:definition '+ttlS(n.definition[k])+'@'+k);});
    if(n.status)P.push('lab:status '+ttlS(n.status)); if(n.level!=null)P.push('lab:level '+n.level);
    if(n.anchor)P.push('lab:anchor '+ttlS(n.anchor));
    (out[n.id]||[]).forEach(function(e){P.push(ttlI(e.p)+' '+ttlI(e.o)); if(e.p==='lab:broader')P.push('skos:broader '+ttlI(e.o));});
    L.push(ttlI(n.id)+'\n  '+P.join(' ;\n  ')+' .\n');});
  return L.join('\n');
}
function csvq(v){v=v==null?'':String(v); return /[",\n]/.test(v)?'"'+v.replace(/"/g,'""')+'"':v;}
function toNodesCsv(g){return ['id,type,label_ko,label_en,status,level,family,page,anchor,coverage,confidence'].concat(g.nodes.map(function(n){
  return [n.id,n.type,n.label&&n.label.ko,n.label&&n.label.en,n.status,n.level,n.family,n.page,n.anchor,n.coverage,n.confidence].map(csvq).join(',');})).join('\r\n');}
function toEdgesCsv(g){return ['source,predicate,target,anchor,confidence'].concat(g.edges.map(function(e){return [e.s,e.p,e.o,e.anchor,e.confidence].map(csvq).join(',');})).join('\r\n');}
function toMermaid(g){
  var keep=g.nodes.filter(function(n){return n.type!=='QuizItem'&&n.type!=='Simulation'&&n.type!=='Work';}).slice(0,40);
  var ix={}; keep.forEach(function(n,i){ix[n.id]='n'+i;});
  var L=['graph LR']; keep.forEach(function(n){L.push('  '+ix[n.id]+'["'+lab(n).replace(/"/g,"'")+'"]');});
  g.edges.forEach(function(e){ if(ix[e.s]&&ix[e.o])L.push('  '+ix[e.s]+' -- '+(REL[pn(e.p)]||pn(e.p))+' --> '+ix[e.o]);});
  return L.join('\n');
}
function toProvCsv(g,refs){
  var R={}; refs.forEach(function(r){R[r.id]=r;});
  var L=['item,kind,work,loc,confidence,verified,pageAnchor'];
  g.nodes.forEach(function(n){(n.source||[]).forEach(function(s){ var r=R[s.ref]; var v=r&&r.lab&&r.lab.verified;
    L.push([n.id,'node',s.ref,s.loc||'',n.confidence,v?(v.title&&v.year&&v.venue?'bib-checked':'partial'):'no',n.anchor].map(csvq).join(','));});});
  g.edges.forEach(function(e){ if(e.p==='lab:assertedIn')L.push([e.s+' '+e.p+' '+e.o,'edge',e.o.replace('lab:work/',''),'',e.confidence,'',e.anchor].map(csvq).join(','));});
  return L.join('\r\n');
}
/* CSL → BibTeX · RIS · 문장 */
var BIBT={'article-journal':'article','paper-conference':'inproceedings','book':'book','chapter':'incollection','webpage':'misc','dataset':'misc','report':'techreport','thesis':'phdthesis','software':'misc'};
var RIST={'article-journal':'JOUR','paper-conference':'CPAPER','book':'BOOK','chapter':'CHAP','webpage':'ELEC','dataset':'DATA','report':'RPRT','thesis':'THES','software':'COMP'};
function names(a){return (a||[]).map(function(p){return p.literal||(p.family+(p.given?', '+p.given:''));});}
function yr(r){return r.issued&&r.issued['date-parts']&&r.issued['date-parts'][0][0];}
function toBib(r){var f=[],add=function(k,v){ if(v!==undefined&&v!==null&&v!=='')f.push('  '+k+' = {'+v+'}');};
  add('title',r.title); add('author',names(r.author).map(function(n){return n==='et al.'?'others':n;}).join(' and ')); add('year',yr(r));
  add(r.type==='article-journal'?'journal':'booktitle',r['container-title']); add('volume',r.volume); add('number',r.issue);
  add('pages',(r.page||'').replace('-','--')); add('publisher',r.publisher); add('doi',r.DOI); add('url',r.URL);
  if(r.lab&&r.lab.note)add('note',r.lab.note);
  return '@'+(BIBT[r.type]||'misc')+'{'+r.id+',\n'+f.join(',\n')+'\n}';}
function toRis(r){var L=['TY  - '+(RIST[r.type]||'GEN')],add=function(t,v){ if(v)L.push(t+'  - '+v);};
  add('TI',r.title); names(r.author).forEach(function(n){add('AU',n);}); add('PY',yr(r)); add('T2',r['container-title']);
  add('VL',r.volume); add('IS',r.issue); var pg=(r.page||'').split('-'); add('SP',pg[0]); add('EP',pg[1]); add('DO',r.DOI); add('UR',r.URL);
  if(r.lab&&r.lab.note)add('N1',r.lab.note); L.push('ER  - '); return L.join('\r\n');}
function toText(r){ var a=names(r.author), first=a[0]?a[0].split(',')[0]:''; var au=a.length>2||a.indexOf('et al.')>=0?first+' 외':a.map(function(x){return x.split(',')[0];}).join(' & ');
  return au+' ('+(yr(r)||'연도 미상')+'). '+r.title+'. '+(r['container-title']||'')+(r.volume?', '+r.volume:'')+(r.issue?'('+r.issue+')':'')+(r.page?', '+r.page:'')+'.'+(r.DOI?' https://doi.org/'+r.DOI:'');}
function pageBib(m){var f=['  title = {'+m.title+'}','  year = {'+m.date.slice(0,4)+'}','  howpublished = {'+m.series+' '+m.number+', v'+m.version+'}'];
  if(m.creator&&m.creator.length&&m.creator[0].name)f.unshift('  author = {'+m.creator.map(function(c){return c.name;}).join(' and ')+'}'); if(m.url)f.push('  url = {'+m.url+'}');
  return '@misc{lab_page_'+m.number+',\n'+f.join(',\n')+'\n}';}
function pageRis(m){var L=['TY  - ELEC','TI  - '+m.title]; (m.creator||[]).forEach(function(c){ if(c.name)L.push('AU  - '+c.name);}); L.push('PY  - '+m.date.slice(0,4),'T2  - '+m.series,'ET  - '+m.version); if(m.url)L.push('UR  - '+m.url); L.push('ER  - '); return L.join('\r\n');}
function pageText(m){ var who=(m.creator||[]).filter(function(c){return c.name;}).map(function(c){return c.name;}).join(', ')||'{저자}';
  return who+' ('+m.date.slice(0,4)+'). '+m.title+'. '+m.series+' '+m.number+', v'+m.version+'.'+(m.url?' '+m.url:'');}

/* ── ZIP (압축 없음) ─────────────────────────────────── */
var CRC=(function(){var t=[],c;for(var n=0;n<256;n++){c=n;for(var k=0;k<8;k++)c=c&1?0xEDB88320^(c>>>1):c>>>1;t[n]=c>>>0;}
  return function(u8){var x=0xFFFFFFFF;for(var i=0;i<u8.length;i++)x=t[(x^u8[i])&255]^(x>>>8);return (x^0xFFFFFFFF)>>>0;};})();
function makeZip(files){
  var enc=new TextEncoder(),parts=[],central=[],off=0;
  function u16(v){return [v&255,(v>>8)&255];} function u32(v){return [v&255,(v>>8)&255,(v>>16)&255,(v>>>24)&255];}
  files.forEach(function(f){var name=enc.encode(f.name),data=enc.encode(f.text),crc=CRC(data);
    var head=[].concat(u32(0x04034b50),u16(20),u16(0x0800),u16(0),u16(0),u16(0),u32(crc),u32(data.length),u32(data.length),u16(name.length),u16(0));
    parts.push(new Uint8Array(head),name,data);
    central.push(new Uint8Array([].concat(u32(0x02014b50),u16(20),u16(20),u16(0x0800),u16(0),u16(0),u16(0),u32(crc),u32(data.length),u32(data.length),
      u16(name.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(off))),name);
    off+=head.length+name.length+data.length;});
  var cdLen=0; central.forEach(function(c){parts.push(c); cdLen+=c.length;});
  parts.push(new Uint8Array([].concat(u32(0x06054b50),u16(0),u16(0),u16(files.length),u16(files.length),u32(cdLen),u32(off),u16(0))));
  return new Blob(parts,{type:'application/zip'});
}
/* 내려받기: claude.ai 아티팩트 안에서는 downloads 능력, 파일로 열면 일반 링크 */
var DLP=(window.claude&&typeof window.claude.use==='function')?window.claude.use('downloads').catch(function(){return null;}):Promise.resolve(null);
var OKX=/\.(json|txt|csv|md|zip|html|svg|pdf)$/i;
function anchorSave(blob,name){var a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=name;
  document.body.appendChild(a); a.click(); setTimeout(function(){URL.revokeObjectURL(a.href); a.remove();},800);}
function download(blob,name){
  return DLP.then(function(d){
    if(!d){anchorSave(blob,name); return;}
    var fn=OKX.test(name)?name:name+'.txt';   // .bib .ris .ttl .jsonld 은 .txt를 붙여 저장 (확장자만 지우면 원래 형식)
    return d.save({filename:fn,data:blob}).catch(function(e){ if(e&&e.code==='declined')return;
      if(e&&(e.code==='unavailable'||e.code==='not_granted'))anchorSave(blob,name);
      else console.warn('저장 실패',e&&e.code);});
  });
}
function dlText(text,name,type){download(new Blob([text],{type:(type||'text/plain')+';charset=utf-8'}),name);}

/* ── 범위 ───────────────────────────────────────────── */
function filterScope(KG,scope){
  if(scope==='all')return KG;
  var keepT={terms:{Concept:1,Method:1,BioAnalogue:1,Limitation:1,Task:1,Metric:1,Dataset:1},
             claims:{Claim:1,Work:1},prereq:null}[scope];
  var nodes,edges;
  if(scope==='prereq'){ edges=KG.edges.filter(function(e){return e.p==='lab:prerequisiteOf'||e.p==='lab:hasLimitation'||e.p==='lab:addressedBy';});
    var ids={}; edges.forEach(function(e){ids[e.s]=1;ids[e.o]=1;}); nodes=KG.nodes.filter(function(n){return ids[n.id];}); }
  else { nodes=KG.nodes.filter(function(n){return keepT[n.type];}); var ix={}; nodes.forEach(function(n){ix[n.id]=1;});
    if(scope==='claims'){ KG.edges.forEach(function(e){ if(e.p==='lab:supports'&&ix[e.s])ix[e.o]=2;});
      nodes=KG.nodes.filter(function(n){return ix[n.id];}); }
    edges=KG.edges.filter(function(e){return ix[e.s]&&(ix[e.o]||/^lab:(topic|area)\//.test(e.o));}); }
  return {version:KG.version,page:KG.page,scope:scope,nodes:nodes,edges:edges};
}
function readme(meta,g,refs){
  var un=refs.filter(function(r){var v=r.lab&&r.lab.verified; return !v||Object.keys(v).some(function(k){return !v[k];});});
  return ['온톨로지·서지 꾸러미 — '+meta.title,'시리즈: '+meta.series+' '+meta.number+' · 버전 '+meta.version+' · 만든 날 '+meta.date,'',
   '범위: '+(g.scope||'all')+' · 노드 '+g.nodes.length+' · 관계 '+g.edges.length+' · 문헌 '+refs.length,'',
   '[파일]','manifest.json 목록 · page_meta.json 페이지 서지 · kg.json 중립 그래프(원본) · kg.jsonld JSON-LD · kg.ttl Turtle',
   'nodes.csv / edges.csv 표(UTF-8 BOM) · references.csl.json 참고문헌 원본 · references.bib BibTeX · references.ris RIS',
   'provenance.csv 주장↔문헌 대응 · mermaid.md 그림용','',
   '[이 페이지 인용]',pageText(meta),'',
   '[확인 필요]',(un.length?un.map(function(r){var v=r.lab.verified;return '- '+r.id+': '+Object.keys(v).filter(function(k){return !v[k];}).join(', ');}).join('\n'):'- 문헌 서지 항목 모두 확인됨'),
   '- 주장(Claim)의 원문 위치(쪽·그림 번호)는 아직 비어 있다. 원문을 보고 provenance.csv의 loc를 채울 것.',
   '- 페이지 저자 이름·라이선스·공개 주소는 비워 두었다. 사용자가 채워 넣을 것.','',
   '[규칙] lab: 접두어 IRI는 '+NS+' (임시). 외부 온톨로지 ID는 확인한 것만 skos:exactMatch/closeMatch로 넣는다.',
   '[주의] 뼈대 영역(lab:topic/*, lab:area/*)은 작성자 초안이며 공식 분류 체계가 아니다.'].join('\n');
}
function buildPackage(scope){
  var KG=J('kg-raw'),REF=J('refs-csl'),META=J('page-meta'); var g=filterScope(KG,scope);
  var used={}; g.nodes.forEach(function(n){(n.source||[]).forEach(function(s){used[s.ref]=1;}); if(n.type==='Work')used[n.id.replace('lab:work/','')]=1;});
  var refs=scope==='all'?REF:REF.filter(function(r){return used[r.id];});
  var files=[{name:'page_meta.json',text:JSON.stringify(META,null,2)},{name:'kg.json',text:JSON.stringify(g,null,2)},
    {name:'kg.jsonld',text:JSON.stringify(toJsonLd(g,META),null,2)},{name:'kg.ttl',text:toTurtle(g)},
    {name:'nodes.csv',text:'﻿'+toNodesCsv(g)},{name:'edges.csv',text:'﻿'+toEdgesCsv(g)},
    {name:'references.csl.json',text:JSON.stringify(refs,null,2)},{name:'references.bib',text:[pageBib(META)].concat(refs.map(toBib)).join('\n\n')},
    {name:'references.ris',text:[pageRis(META)].concat(refs.map(toRis)).join('\r\n')},{name:'provenance.csv',text:'﻿'+toProvCsv(g,refs)},
    {name:'mermaid.md',text:'```mermaid\n'+toMermaid(g)+'\n```\n'},{name:'README.txt',text:readme(META,g,refs)}];
  files.unshift({name:'manifest.json',text:JSON.stringify({package:'lab-kg',packageVersion:'1.0',page:META.number,pageId:KG.page,pageVersion:META.version,
    registry:META.registry||'',created:META.date,scope:scope,counts:{nodes:g.nodes.length,edges:g.edges.length,refs:refs.length},
    files:files.map(function(f){return f.name;})},null,2)});
  return files;
}

/* ── 공통 화면 조각 ─────────────────────────────────── */
var CSS='.kgx-sec{background:var(--bg,#ffffff);color:var(--text,#16212b);padding:48px 0;font-family:inherit}.kgx-sec .kgx-wrap{max-width:1080px;margin:0 auto;padding:0 16px}.kgx-sec h2{margin:0 0 6px;font-size:24px}.kgx-sec .kgx-sub{color:var(--muted,#5b6874);margin:0 0 18px}\
\
.kgx .tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:10px}\
.kgx input[type=search]{flex:1 1 220px;min-width:0;background:var(--panel2,#eef2f6);border:1px solid var(--rule,#d5dbe2);color:var(--text,#16212b);border-radius:8px;padding:8px 12px;font:inherit;font-size:15px}\
.kgx .tchip{font-size:12.5px;border-radius:999px;padding:3px 10px;border:1px solid var(--rule,#d5dbe2);background:var(--panel2,#eef2f6);color:var(--muted,#5b6874);cursor:pointer}\
.kgx .tchip[aria-pressed=true]{color:#13141f;font-weight:700}\
.kgx .grid2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:16px}\
@media (max-width:860px){.kgx .grid2{grid-template-columns:1fr}}\
.kgx .list{max-height:520px;overflow:auto;border:1px solid var(--rule,#d5dbe2);border-radius:10px;background:var(--panel,#f6f8fa)}\
.kgx .it{padding:10px 14px;border-bottom:1px solid var(--rule,#d5dbe2);cursor:pointer}\
.kgx .it:last-child{border-bottom:0}.kgx .it:hover{background:var(--panel2,#eef2f6)}\
.kgx .it.sel{background:var(--panel2,#eef2f6);box-shadow:inset 3px 0 0 var(--gfp,#13733a)}\
.kgx .it .h{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}\
.kgx .it .nm{font-weight:700}.kgx .it .en{color:var(--muted,#5b6874);font-size:13px}\
.kgx .ty{font-size:11.5px;border-radius:5px;padding:0 6px;color:#13141f;font-weight:700;white-space:nowrap}\
.kgx .it .df{color:#d7d4e6;font-size:14px;margin:3px 0 0}\
.kgx .it .more{display:none;margin-top:6px;font-size:13.5px;color:var(--muted,#5b6874)}.kgx .it.sel .more{display:block}\
.kgx .it a{color:var(--gfp,#13733a)}\
.kgx .rel{display:inline-block;margin:2px 6px 2px 0;padding:1px 8px;border-radius:6px;background:var(--bg,#ffffff);border:1px solid var(--rule,#d5dbe2);font-size:12.5px;cursor:pointer;color:var(--text,#16212b)}\
.kgx .gbox{position:relative;border:1px solid var(--rule,#d5dbe2);border-radius:10px;background:#101119;overflow:hidden}\
.kgx .gbox canvas{display:block;width:100%;height:420px}\
.kgx .legend{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px;color:var(--muted,#5b6874);margin-top:8px}\
.kgx .legend i{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:4px;vertical-align:-1px}\
.kgx .path{display:flex;flex-wrap:wrap;gap:6px;align-items:center}\
.kgx .path span.s{background:var(--panel2,#eef2f6);border:1px solid var(--rule,#d5dbe2);border-radius:8px;padding:4px 10px;font-size:14px}\
.kgx .path span.a{color:var(--muted,#5b6874)}.kgx .path span.lim{border-color:var(--eye,#c9302c);color:var(--eye,#c9302c)}\
.kgx .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin-bottom:14px}\
.kgx .stats div{background:var(--panel,#f6f8fa);border:1px solid var(--rule,#d5dbe2);border-radius:10px;padding:10px 12px}\
.kgx .stats b{display:block;font-size:24px;font-variant-numeric:tabular-nums}.kgx .stats span{color:var(--muted,#5b6874);font-size:13px}\
.kgx .say{display:flex;gap:12px;align-items:flex-start;margin:6px 0 14px;background:var(--panel,#f6f8fa);border:1px solid var(--rule,#d5dbe2);border-left:4px solid var(--who,var(--c-asst,#c42a6e));border-radius:14px;padding:10px 14px}\
.kgx .say img{flex:none;width:64px;height:64px;border-radius:10px;background:#fff;object-fit:contain}\
.kgx .say .name{display:block;color:var(--who,var(--c-asst,#c42a6e));font-size:14px}\
.kgx .say p{margin:.15em 0 0;font-size:15px}\
.kgx .refs .r{padding:12px 14px;border-bottom:1px solid var(--rule,#d5dbe2)}.kgx .refs .r:last-child{border-bottom:0}\
.kgx .badge{display:inline-block;font-size:11.5px;border-radius:5px;padding:0 6px;margin-left:6px;font-weight:700}\
.kgx .badge.ok{background:var(--gfp,#13733a);color:var(--bg,#ffffff)}.kgx .badge.no{background:transparent;border:1px solid var(--amber,#a35c00);color:var(--amber,#a35c00)}\
.kgx .badge.role{background:var(--panel2,#eef2f6);color:var(--muted,#5b6874);border:1px solid var(--rule,#d5dbe2)}\
.kgx pre.cite{white-space:pre-wrap;word-break:break-word;background:var(--panel2,#eef2f6);border:1px solid var(--rule,#d5dbe2);border-radius:8px;padding:10px 12px;font-size:13px;margin:8px 0;max-height:220px;overflow:auto}\
.kgx .files{display:flex;flex-wrap:wrap;gap:6px}\
.kgx .todo li{margin:4px 0;color:#d7d4e6}\
.kgx h3{font-size:17px;margin:20px 0 8px}\
';
function addCss(){ if($id('kgx-css'))return; var s=el('style'); s.id='kgx-css'; s.textContent=CSS; document.head.appendChild(s);}
function copy(text,btn){ function ok(){var o=btn.textContent; btn.textContent='복사됨'; setTimeout(function(){btn.textContent=o;},1200);}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(text).then(ok,fallback);} else fallback();
  function fallback(){var p=btn.parentNode.parentNode.querySelector('pre.cite'); if(p){var r=document.createRange(); r.selectNodeContents(p); var s=getSelection(); s.removeAllRanges(); s.addRange(r);} btn.textContent='선택됨 — Ctrl+C';}}

/* ── 지식 색인 ──────────────────────────────────────── */
function mountIndex(root){
  var KG=J('kg-raw'); var N={},OUT={},IN={};
  KG.nodes.forEach(function(n){N[n.id]=n;OUT[n.id]=[];IN[n.id]=[];});
  KG.edges.forEach(function(e){ if(OUT[e.s])OUT[e.s].push(e); if(IN[e.o])IN[e.o].push(e);});
  var types=Object.keys(KG.nodes.reduce(function(a,n){a[n.type]=(a[n.type]||0)+1;return a;},{}));
  var count={}; KG.nodes.forEach(function(n){count[n.type]=(count[n.type]||0)+1;});
  var on={}; types.forEach(function(t){on[t]=t!=='QuizItem'&&t!=='Simulation'&&t!=='Work';});
  var sel=null,q='';
  root.classList.add('kgx');
  var topics=0; KG.edges.forEach(function(e){if(e.p==='lab:broader')topics++;});
  var claims=KG.nodes.filter(function(n){return n.type==='Claim';}), csrc=claims.filter(function(n){return (n.source||[]).length;}).length;
  root.innerHTML='<div class="stats"><div><b>'+KG.nodes.length+'</b><span>항목(노드)</span></div><div><b>'+KG.edges.length+'</b><span>관계</span></div>'+
    '<div><b>'+(count.Concept||0)+(count.Method||0)+'</b><span>개념·방법</span></div><div><b>'+(count.BioAnalogue||0)+'</b><span>생물 대응</span></div>'+
    '<div><b>'+csrc+'/'+claims.length+'</b><span>출처 있는 주장</span></div><div><b>'+topics+'</b><span>뼈대 주제 연결</span></div></div>'+
    '<div class="tools"><input type="search" placeholder="찾기 — 가중치, overfitting, 케니언, 냄새 기억 노트 …" aria-label="지식 색인 검색"></div>'+
    '<div class="tools chips" role="group" aria-label="종류"></div>'+
    '<div class="grid2"><div class="list" role="listbox" aria-label="검색 결과"></div>'+
    '<div><div class="gbox"><canvas aria-label="선택한 항목과 이웃 관계 그래프"></canvas></div><div class="legend"></div>'+
    '<p class="note gnote">항목을 고르면 그 항목과 바로 이어진 이웃만 보여 준다. 그래프의 점을 눌러도 된다.</p></div></div>'+
    '<h3>개념정리 경로 — 먼저 알아야 할 것과 한계의 사슬</h3><div class="path ladder"></div>'+
    '<h3>열린 질문 · 확인 필요</h3><ul class="todo qs"></ul>';
  // 항목 수 계산 오류 방지: 개념+방법 합
  root.querySelector('.stats div:nth-child(3) b').textContent=(count.Concept||0)+(count.Method||0);
  var inp=root.querySelector('input'), chips=root.querySelector('.chips'), list=root.querySelector('.list'), cv=root.querySelector('canvas');
  types.forEach(function(t){var b=el('button','tchip',tl(t)+' '+count[t]); b.type='button'; b.setAttribute('aria-pressed',on[t]);
    if(on[t])b.style.background=tc(t),b.style.borderColor=tc(t);
    b.onclick=function(){on[t]=!on[t]; b.setAttribute('aria-pressed',on[t]); b.style.background=on[t]?tc(t):''; b.style.borderColor=on[t]?tc(t):''; render();};
    chips.appendChild(b);});
  var lg=root.querySelector('.legend'); types.forEach(function(t){lg.insertAdjacentHTML('beforeend','<span><i style="background:'+tc(t)+'"></i>'+tl(t)+'</span>');});
  lg.insertAdjacentHTML('beforeend','<span>── 화살표: 관계 방향</span>');
  inp.addEventListener('input',function(){q=inp.value.trim().toLowerCase(); render();});
  function hay(n){return [n.id,n.label&&n.label.ko,n.label&&n.label.en,n.definition&&n.definition.ko,n.altLabel&&[].concat(n.altLabel.ko||[]).join(' ')].join(' ').toLowerCase();}
  function relHtml(n){
    var h=[]; OUT[n.id].forEach(function(e){ var o=N[e.o]; var nm=o?lab(o):((KG.topicLabels||{})[e.o]||e.o.replace(/^lab:(topic|area)\//,'').replace(/-/g,' '));
      h.push('<span class="rel" data-go="'+esc(o?e.o:'')+'">'+esc(REL[pn(e.p)]||pn(e.p))+' → '+esc(nm)+'</span>');});
    IN[n.id].forEach(function(e){ var s=N[e.s]; if(!s)return; h.push('<span class="rel" data-go="'+esc(e.s)+'">'+esc(lab(s))+' → '+esc(REL[pn(e.p)]||pn(e.p))+'</span>');});
    return h.join('');}
  function render(){
    var arr=KG.nodes.filter(function(n){return on[n.type]&&(!q||hay(n).indexOf(q)>=0);});
    list.innerHTML=arr.length?'':'<div class="it">찾는 항목이 없다. 종류 칩이 꺼져 있지 않은지 보자.</div>';
    arr.forEach(function(n){var d=el('div','it'+(sel===n.id?' sel':'')); d.setAttribute('role','option'); d.dataset.id=n.id;
      var alt=n.altLabel&&n.altLabel.ko?' · '+[].concat(n.altLabel.ko).join(', '):'';
      var src=(n.source||[]).length?' · 출처 '+n.source.length:'';
      d.innerHTML='<div class="h"><span class="ty" style="background:'+tc(n.type)+'">'+tl(n.type)+'</span><span class="nm">'+esc(lab(n))+'</span><span class="en">'+esc((n.label&&n.label.en)||'')+esc(alt)+'</span></div>'+
        (n.definition?'<p class="df">'+esc(n.definition.ko)+'</p>':'')+
        '<div class="more">'+(n.anchor?'<a href="'+n.anchor+'">설명 보러 가기 →</a>':'')+' <span>'+esc(src)+(n.confidence&&n.confidence!=='high'?' · 확신도 '+n.confidence:'')+'</span><div style="margin-top:6px">'+relHtml(n)+'</div></div>';
      d.onclick=function(ev){var g=ev.target.closest('.rel'); if(g){ if(g.dataset.go)pick(g.dataset.go,true); ev.stopPropagation(); return;}
        if(ev.target.tagName==='A')return; pick(n.id);};
      list.appendChild(d);});
    draw();
  }
  function pick(id,scroll){ sel=id; var n=N[id]; if(n&&!on[n.type]){on[n.type]=true; var b=[].slice.call(chips.children)[types.indexOf(n.type)]; b.setAttribute('aria-pressed',true); b.style.background=tc(n.type); b.style.borderColor=tc(n.type);}
    if(scroll&&q){q='';inp.value='';} render(); var it=list.querySelector('.it.sel'); if(it)it.scrollIntoView({block:'nearest'});}
  // 그래프
  var G={pts:[]};
  function layout(){
    var center=sel||KG.edges.reduce(function(best,e){return best;},null);
    var ids={},pts=[];
    if(!sel){ // 개요: 퀴즈·시뮬·문헌 빼고 연결 많은 순 최대 60
      var deg={}; KG.edges.forEach(function(e){deg[e.s]=(deg[e.s]||0)+1;deg[e.o]=(deg[e.o]||0)+1;});
      KG.nodes.filter(function(n){return on[n.type];}).sort(function(a,b){return (deg[b.id]||0)-(deg[a.id]||0);}).slice(0,60).forEach(function(n){ids[n.id]=1;});
    } else { ids[sel]=1; OUT[sel].forEach(function(e){if(N[e.o])ids[e.o]=1;}); IN[sel].forEach(function(e){ids[e.s]=1;}); }
    var r=mulberry(7); Object.keys(ids).forEach(function(id){pts.push({id:id,x:r()-.5,y:r()-.5,vx:0,vy:0});});
    var ix={}; pts.forEach(function(p,i){ix[p.id]=i;});
    var es=KG.edges.filter(function(e){return ix[e.s]!=null&&ix[e.o]!=null;});
    for(var it=0;it<220;it++){
      for(var i=0;i<pts.length;i++)for(var j=i+1;j<pts.length;j++){var a=pts[i],b=pts[j],dx=a.x-b.x,dy=a.y-b.y,d2=dx*dx+dy*dy+1e-4,f=0.0016/d2;
        a.vx+=dx*f;a.vy+=dy*f;b.vx-=dx*f;b.vy-=dy*f;}
      es.forEach(function(e){var a=pts[ix[e.s]],b=pts[ix[e.o]],dx=b.x-a.x,dy=b.y-a.y,d=Math.sqrt(dx*dx+dy*dy)+1e-6,f=(d-0.22)*0.04;
        a.vx+=dx/d*f;a.vy+=dy/d*f;b.vx-=dx/d*f;b.vy-=dy/d*f;});
      pts.forEach(function(p){ if(p.id===sel){p.x*=.9;p.y*=.9;} p.vx-=p.x*0.004;p.vy-=p.y*0.004; p.x+=p.vx;p.y+=p.vy;p.vx*=.6;p.vy*=.6;});
    }
    G={pts:pts,es:es,ix:ix};
  }
  function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;var t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
  function draw(){
    layout(); var dpr=Math.min(2,window.devicePixelRatio||1), W=cv.clientWidth||600, H=cv.clientHeight||420;
    cv.width=W*dpr; cv.height=H*dpr; var c=cv.getContext('2d'); c.setTransform(dpr,0,0,dpr,0,0); c.clearRect(0,0,W,H);
    var xs=G.pts.map(function(p){return p.x;}),ys=G.pts.map(function(p){return p.y;});
    var mx=Math.min.apply(0,xs),Mx=Math.max.apply(0,xs),my=Math.min.apply(0,ys),My=Math.max.apply(0,ys);
    var pad=54, sx=(W-2*pad)/Math.max(1e-3,Mx-mx), sy=(H-2*pad)/Math.max(1e-3,My-my);
    G.pts.forEach(function(p){p.X=pad+(p.x-mx)*sx; p.Y=pad+(p.y-my)*sy; if(G.pts.length===1){p.X=W/2;p.Y=H/2;}});
    c.lineWidth=1;
    G.es.forEach(function(e){var a=G.pts[G.ix[e.s]],b=G.pts[G.ix[e.o]]; var hot=sel&&(e.s===sel||e.o===sel);
      c.strokeStyle=hot?'rgba(236,234,243,.55)':'rgba(157,155,184,.22)'; c.beginPath(); c.moveTo(a.X,a.Y); c.lineTo(b.X,b.Y); c.stroke();
      var ang=Math.atan2(b.Y-a.Y,b.X-a.X), ex=b.X-Math.cos(ang)*9, ey=b.Y-Math.sin(ang)*9;
      c.fillStyle=c.strokeStyle; c.beginPath(); c.moveTo(ex,ey); c.lineTo(ex-Math.cos(ang-.4)*7,ey-Math.sin(ang-.4)*7); c.lineTo(ex-Math.cos(ang+.4)*7,ey-Math.sin(ang+.4)*7); c.fill();
      if(sel&&hot&&G.pts.length<26){c.fillStyle='#9d9bb8'; c.font='11px '+getComputedStyle(document.body).fontFamily; c.textAlign='center';
        c.fillText(REL[pn(e.p)]||pn(e.p),(a.X+b.X)/2,(a.Y+b.Y)/2-4);} });
    c.textAlign='center'; c.font='12.5px '+getComputedStyle(document.body).fontFamily;
    G.pts.forEach(function(p){var n=N[p.id]; var R=p.id===sel?9:6; c.fillStyle=tc(n.type); c.beginPath(); c.arc(p.X,p.Y,R,0,7); c.fill();
      if(p.id===sel){c.strokeStyle='#eceaf3';c.lineWidth=2;c.stroke();c.lineWidth=1;}
      var t=lab(n); if(t.length>14)t=t.slice(0,13)+'…'; c.fillStyle=p.id===sel?'#fff':'#d7d4e6'; c.fillText(t,p.X,p.Y-R-5);});
    c.fillStyle='rgba(241,182,70,.9)'; c.font='11px '+getComputedStyle(document.body).fontFamily; c.textAlign='left';
    c.fillText(sel?'이웃 '+(G.pts.length-1)+'개':'개요 — 연결 많은 항목 '+G.pts.length+'개',10,18);
  }
  cv.addEventListener('click',function(ev){var r=cv.getBoundingClientRect(),x=ev.clientX-r.left,y=ev.clientY-r.top,best=null,bd=400;
    G.pts.forEach(function(p){var d=(p.X-x)*(p.X-x)+(p.Y-y)*(p.Y-y); if(d<bd){bd=d;best=p;}}); if(best)pick(best.id,true);});
  var rt; window.addEventListener('resize',function(){clearTimeout(rt); rt=setTimeout(draw,150);});
  // 개념정리 경로
  var lad=root.querySelector('.ladder'), chainE=KG.edges.filter(function(e){return (e.p==='lab:prerequisiteOf'&&N[e.s].type==='Method'&&N[e.o]&&N[e.o].type==='Method');});
  var nexts={},has={}; chainE.forEach(function(e){nexts[e.s]=e.o;has[e.o]=1;});
  var start=Object.keys(nexts).filter(function(k){return !has[k];})[0], seen={};
  var html=[]; for(var cur=start;cur&&!seen[cur];cur=nexts[cur]){ seen[cur]=1;
    html.push('<span class="s" data-go="'+cur+'" style="border-color:'+tc('Method')+'">'+esc(lab(N[cur]))+'</span>');
    var lim=OUT[cur].filter(function(e){return e.p==='lab:hasLimitation';})[0];
    if(lim)html.push('<span class="a">→ 한계</span><span class="s lim" data-go="'+lim.o+'">'+esc(lab(N[lim.o]))+'</span>');
    if(nexts[cur])html.push('<span class="a">→ 해결</span>');}
  lad.innerHTML=html.length?html.join(''):'<span class="note">이 페이지에는 개념정리 사슬이 없다.</span>';
  lad.addEventListener('click',function(ev){var s=ev.target.closest('[data-go]'); if(s)pick(s.dataset.go,true);});
  var qs=root.querySelector('.qs'); KG.nodes.filter(function(n){return n.type==='Question';}).forEach(function(n){
    var li=el('li',null,'<b>'+esc(lab(n))+'</b>'+(n.definition?' — '+esc(n.definition.ko):'')+(n.confidence==='low'?' <span class="badge no">확인 필요</span>':'')+(n.anchor?' <a href="'+n.anchor+'" style="color:var(--gfp,#13733a)">본문</a>':''));
    qs.appendChild(li);});
  render();
}

/* ── 꾸러미 ─────────────────────────────────────────── */
/* 조수 말풍선 그림: 페이지의 캐릭터 그림(Cast 또는 SPRITE)을 쓴다. 글자 상자로 대신하지 않는다. */
function asstSrc(){var s='';try{
  if(window.Cast&&Cast.src)s=Cast.src('asst','e13')||Cast.src('asst','smile')||'';
  if(!s&&window.SPRITE){var A=window.SPRITE_ALIAS||{};var S=window.SPRITE;s=S[A.asst_e13||'asst_e13']||S[A.asst_smile||'asst_smile']||'';}
  if(!s&&window.LAB_PACK&&LAB_PACK.img){var I=LAB_PACK.img,L=LAB_PACK.alias||{};s=I.asst_e13||I[L.asst_smile||'asst_smile']||'';}
}catch(e){} return s;}
function mountExport(root){
  var KG=J('kg-raw'),REF=J('refs-csl'),META=J('page-meta'); root.classList.add('kgx');
  var verifiedAll=function(r){var v=r.lab&&r.lab.verified; return v&&Object.keys(v).every(function(k){return v[k];});};
  var vb=REF.filter(verifiedAll).length;
  var claims=KG.nodes.filter(function(n){return n.type==='Claim';});
  var todo=[]; REF.forEach(function(r){var v=r.lab&&r.lab.verified||{}; Object.keys(v).forEach(function(k){if(!v[k])todo.push(r.id+' — '+k+' 미확인 (공란으로 둠)');});});
  todo.push('주장 '+claims.length+'개의 원문 위치(쪽·그림 번호) — provenance.csv의 loc 항목이 비어 있음');
  todo.push('페이지 저자 이름·라이선스·공개 주소 — page_meta.json에서 비워 둠');
  var sup={}; KG.edges.forEach(function(e){ if(e.p==='lab:assertedIn'){var k=e.o.replace('lab:work/',''); (sup[k]=sup[k]||[]).push(e.s);} });
  KG.nodes.forEach(function(n){(n.source||[]).forEach(function(s){(sup[s.ref]=sup[s.ref]||[]); if(sup[s.ref].indexOf(n.id)<0)sup[s.ref].push(n.id);});});
  var N={}; KG.nodes.forEach(function(n){N[n.id]=n;});
  var asrc=asstSrc();
  root.innerHTML='<div class="say" data-who="asst"><img data-who="asst" data-mood="e13" alt="" aria-hidden="true"'+(asrc?' src="'+asrc+'"':'')+'><div><b class="name">조수(하루)</b><p>출처 없는 주장은 꾸러미에 넣지 않았어요. 사람이 확인할 항목 '+todo.length+'개는 아래에 있어요.</p></div></div>'+
    '<div class="stats"><div><b>'+KG.nodes.length+'</b><span>노드</span></div><div><b>'+KG.edges.length+'</b><span>관계</span></div><div><b>'+REF.length+'</b><span>문헌</span></div>'+
    '<div><b>'+Math.round(100*vb/Math.max(1,REF.length))+'%</b><span>서지 전부 확인된 문헌</span></div>'+
    '<div><b>'+Math.round(100*claims.filter(function(n){return (n.source||[]).length;}).length/Math.max(1,claims.length))+'%</b><span>출처 있는 주장</span></div></div>'+
    '<h3>이 페이지 인용하기</h3><div class="tools"><button class="tchip cf" data-f="text" aria-pressed="true" style="background:var(--gfp,#13733a);border-color:var(--gfp,#13733a);color:var(--bg,#ffffff)">일반 문장</button><button class="tchip cf" data-f="bib" aria-pressed="false">BibTeX</button><button class="tchip cf" data-f="ris" aria-pressed="false">RIS</button><button class="bt cp" type="button">복사</button></div><pre class="cite pc"></pre>'+
    '<h3>참고문헌 — 확인 배지와 뒷받침하는 개념</h3><div class="refs list"></div>'+
    '<h3>범위와 형식 고르기</h3><div class="tools sc" role="group" aria-label="범위"></div><div class="tools"><button class="bt primary zip" type="button">꾸러미 ZIP 내려받기</button><span class="note zc"></span></div>'+
    '<div class="files"></div><p class="note">claude.ai 화면에서 개별 파일을 받으면 .bib·.ris·.ttl·.jsonld 이름 끝에 .txt가 붙는다(끝의 .txt만 지우면 원래 형식). ZIP 안의 파일은 원래 이름 그대로다.</p>'+
    (META.seeAlso?'<p class="note">여러 페이지의 꾸러미를 합쳐 영역 지도와 맞대어 보려면 → <a style="color:var(--gfp,#13733a)" href="'+esc(META.seeAlso)+'"'+(/^https?:/.test(META.seeAlso)?' target="_blank" rel="noopener"':'')+'>영역 지도 합치기 (KG_00)</a></p>':'')+
    '<h3>사람이 확인할 항목</h3><ul class="todo">'+todo.map(function(t){return '<li>'+esc(t)+'</li>';}).join('')+'</ul>'+
    '<p class="note">꾸러미 버전 1.0 · 만든 날 '+esc(META.date)+' · 등록부 '+esc(META.registry||'KG_00_registry (시제품)')+' · lab: 접두어 '+NS+' (임시) · 뼈대 주제(lab:topic/*)는 작성자 초안</p>';
  var fmt='text', pc=root.querySelector('.pc');
  function cite(){pc.textContent=fmt==='bib'?pageBib(META):fmt==='ris'?pageRis(META):pageText(META);}
  [].forEach.call(root.querySelectorAll('.cf'),function(b){b.onclick=function(){fmt=b.dataset.f; [].forEach.call(root.querySelectorAll('.cf'),function(x){var o=x===b; x.setAttribute('aria-pressed',o); x.style.background=o?'var(--gfp,#13733a)':''; x.style.borderColor=o?'var(--gfp,#13733a)':'';}); cite();};});
  root.querySelector('.cp').onclick=function(){copy(pc.textContent,this);}; cite();
  var RL=root.querySelector('.refs');
  REF.forEach(function(r){var v=r.lab&&r.lab.verified||{}; var bad=Object.keys(v).filter(function(k){return !v[k];});
    var d=el('div','r','<div>'+esc(toText(r))+'<span class="badge role">'+esc({primary:'주 자료',background:'배경',data:'수치',figure:'그림'}[r.lab&&r.lab.role]||'배경')+'</span>'+
      (bad.length?'<span class="badge no">확인 필요: '+esc(bad.join(', '))+'</span>':'<span class="badge ok">서지 확인됨</span>')+'</div>'+
      '<div style="margin-top:6px">'+(sup[r.id]||[]).map(function(id){var n=N[id]; return n?'<a class="rel" href="'+(n.anchor||'#kg')+'">'+esc(lab(n))+'</a>':'';}).join('')+'</div>');
    RL.appendChild(d);});
  var scope='all', SC=root.querySelector('.sc'), zc=root.querySelector('.zc');
  [['all','전체'],['terms','개념·방법만'],['claims','주장 + 출처만'],['prereq','선수 관계만']].forEach(function(s,i){
    var b=el('button','tchip',s[1]); b.type='button'; b.setAttribute('aria-pressed',i===0); if(i===0)b.style.background='var(--gfp,#13733a)',b.style.borderColor='var(--gfp,#13733a)';
    b.onclick=function(){scope=s[0]; [].forEach.call(SC.children,function(x){var o=x===b; x.setAttribute('aria-pressed',o); x.style.background=o?'var(--gfp,#13733a)':''; x.style.borderColor=o?'var(--gfp,#13733a)':'';}); info();};
    SC.appendChild(b);});
  var FL=root.querySelector('.files');
  function info(){var f=buildPackage(scope), m=JSON.parse(f[0].text); zc.textContent='노드 '+m.counts.nodes+' · 관계 '+m.counts.edges+' · 문헌 '+m.counts.refs+' · 파일 '+f.length+'개';
    FL.innerHTML=''; f.forEach(function(x){var b=el('button','bt',esc(x.name)); b.type='button'; b.onclick=function(){dlText(x.text,x.name);}; FL.appendChild(b);});}
  root.querySelector('.zip').onclick=function(){download(makeZip(buildPackage(scope)),'kg_'+META.number+'_'+scope+'.zip');};
  info();
}
function init(){addCss(); var a=$id('kg-mount'),b=$id('export-mount'); if(a)mountIndex(a); if(b)mountExport(b);
  if(window.Cast&&Cast.fill)Cast.fill();
  setTimeout(function(){var im=b&&b.querySelector('.say img[data-who]'); if(im&&!im.getAttribute('src'))im.remove();},0);}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init); else init();
return {download:download,buildPackage:buildPackage,makeZip:makeZip,toJsonLd:toJsonLd,toTurtle:toTurtle,toBib:toBib,toRis:toRis};
})();
