#!/usr/bin/env python3
"""Generate the frontend/index.html file with msapp + fragment support."""
from pathlib import Path

# Split into parts to stay manageable
CSS = r"""*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0c0e14;--sfc:#141720;--sfc2:#1a1e2b;--brd:#252a3a;--txt:#e0e3ec;--mut:#7a7f94;--acc:#5b7fff;--accH:#7b9bff;--accD:#2d3f7a;--ok:#4ade80;--warn:#f59e0b;--err:#ef4444;--code:#a5b4fc;--mono:'Cascadia Code','Fira Code','Consolas',monospace}
body{font-family:'Segoe UI',-apple-system,system-ui,sans-serif;background:var(--bg);color:var(--txt);min-height:100vh;display:flex;flex-direction:column}
.hdr{background:var(--sfc);border-bottom:1px solid var(--brd);padding:14px 28px;display:flex;align-items:center;gap:16px}
.logo{font-size:22px;font-weight:700;color:var(--acc)}.logo-s{font-size:12px;color:var(--mut)}
.mn{display:flex;flex:1;overflow:hidden}
.sb{width:220px;background:var(--sfc);border-right:1px solid var(--brd);padding:16px 0;flex-shrink:0;display:flex;flex-direction:column}
.si{padding:10px 24px;cursor:pointer;font-size:14px;color:var(--mut);border-right:3px solid transparent;transition:all .15s}
.si:hover{color:var(--accH);background:rgba(91,127,255,.05)}
.si.a{color:var(--acc);background:rgba(91,127,255,.1);border-right-color:var(--acc);font-weight:600}
.ct{flex:1;overflow:auto;padding:28px 36px}
.wf{padding:16px 24px;border-top:1px solid var(--brd);margin-top:auto;font-size:11px;color:var(--mut);line-height:1.7}
.cd{background:var(--sfc);border:1px solid var(--brd);border-radius:10px;padding:24px 28px;margin-bottom:20px}
.cdt{font-size:18px;font-weight:600;margin-bottom:12px}
.btn{padding:10px 20px;border:none;border-radius:7px;cursor:pointer;font-size:14px;font-weight:600;transition:all .15s}
.bp{background:var(--acc);color:#fff}.bp:hover{background:var(--accH)}
.bo{background:transparent;color:var(--acc);border:1px solid var(--acc)}.bo:hover{background:rgba(91,127,255,.1)}
.bg{background:var(--sfc2);color:var(--mut)}.bg:hover{background:var(--brd)}
.bs{padding:6px 14px;font-size:12px}
.btn:disabled{opacity:.5;cursor:not-allowed}
.inp{width:100%;padding:10px 14px;background:var(--sfc2);border:1px solid var(--brd);border-radius:7px;color:var(--txt);font-size:14px;outline:none;font-family:inherit}.inp:focus{border-color:var(--acc)}
.ta{min-height:280px;font-family:var(--mono);font-size:13px;color:var(--code);resize:vertical;line-height:1.6}
.tas{min-height:60px}
.lb{font-size:13px;font-weight:600;color:var(--mut);margin-bottom:6px;display:block}
.sel{padding:8px 12px;background:var(--sfc2);color:var(--txt);border:1px solid var(--brd);border-radius:6px;font-size:14px;outline:none}
.sts{display:flex;gap:12px;flex-wrap:wrap;margin-top:16px}
.st{display:flex;flex-direction:column;align-items:center;padding:16px 20px;background:var(--sfc2);border-radius:8px;min-width:100px}
.sn{font-size:28px;font-weight:700;color:var(--acc)}.sl{font-size:11px;color:var(--mut);margin-top:4px;text-transform:uppercase;letter-spacing:.5px}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;padding:8px 12px;background:var(--sfc2);border-bottom:1px solid var(--brd);color:var(--mut);font-weight:600;font-size:11px;text-transform:uppercase;letter-spacing:.5px}
td{padding:8px 12px;border-bottom:1px solid rgba(37,42,58,.3);vertical-align:top}
.dz{border:2px dashed var(--brd);border-radius:10px;padding:40px 20px;text-align:center;color:var(--mut);cursor:pointer;transition:all .2s}
.dz.ov{border-color:var(--acc);color:var(--acc);background:rgba(91,127,255,.05)}
.badge{display:inline-block;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600;color:#fff}
.b-ok{background:var(--ok)}.b-er{background:var(--err)}.b-wa{background:var(--warn)}.b-in{background:var(--accD)}
.b-msapp{background:#9333ea}.b-frag{background:#0ea5e9}
.tst{position:fixed;bottom:24px;right:24px;padding:14px 24px;border-radius:8px;font-size:14px;font-weight:500;z-index:9999;color:#fff;box-shadow:0 4px 20px rgba(0,0,0,.4);animation:si .3s}
@keyframes si{from{transform:translateX(100px);opacity:0}to{transform:translateX(0);opacity:1}}
.dv{display:flex;align-items:center;gap:12px;margin:20px 0 8px}.dv-l{flex:1;height:1px;background:var(--brd)}
.f{display:flex}.g6{gap:6px}.g10{gap:10px}.g16{gap:16px}.fw{flex-wrap:wrap}
.mt12{margin-top:12px}.mt16{margin-top:16px}.mb8{margin-bottom:8px}.mb16{margin-bottom:16px}
.pre{background:var(--sfc2);padding:16px;border-radius:8px;overflow:auto;max-height:600px;font-size:12px;font-family:var(--mono);color:var(--code);line-height:1.5;white-space:pre-wrap}
.ifr{width:100%;border:none;border-radius:8px;background:var(--sfc2);min-height:600px}
.it{max-height:60px;border-radius:4px;margin-left:10px;vertical-align:middle}
.dl{display:inline-block;padding:6px 14px;background:var(--sfc2);border-radius:6px;color:var(--acc);text-decoration:none;font-size:13px;font-weight:500}.dl:hover{background:var(--brd)}
.chk{display:flex;align-items:center;gap:10px;cursor:pointer;font-size:14px;margin-bottom:10px}
.fd{margin-bottom:10px;padding:10px;border-radius:6px;border-left:3px solid var(--acc)}
.fd-w{background:rgba(245,158,11,.08);border-left-color:var(--warn)}.fd-i{background:var(--sfc2)}
.sc{margin-bottom:16px;padding:14px;background:var(--sfc2);border-radius:8px}
.mode-sel{display:flex;gap:4px;padding:2px;background:var(--sfc2);border-radius:8px;border:1px solid var(--brd)}
.mode-opt{padding:7px 14px;border-radius:6px;cursor:pointer;font-size:13px;color:var(--mut);transition:all .15s;border:none;background:transparent;font-weight:500}
.mode-opt.act{background:var(--acc);color:#fff}
.info-banner{padding:10px 16px;border-radius:8px;font-size:13px;margin-bottom:16px;display:flex;align-items:center;gap:10px}
.info-banner.frag{background:rgba(14,165,233,.1);border:1px solid rgba(14,165,233,.3);color:#38bdf8}
.info-banner.msapp{background:rgba(147,51,234,.1);border:1px solid rgba(147,51,234,.3);color:#a78bfa}"""

SAMPLE = r"""App:
  Name: Urlaubsantrag-App
  Properties:
    AppVersion: "1.2.3"
    Author: "Max Mustermann"
    OnStart: |
      ClearCollect(colMitarbeiter, Office365Users.SearchUser({searchTerm: "", top: 100}));
      Set(varCurrentUser, Office365Users.MyProfile());
      Set(varIsManager, false);
      ClearCollect(colUrlaubsantraege, Filter('Urlaubsantraege', Mitarbeiter.Email = varCurrentUser.Mail));
Screens:
  HomeScreen:
    Control: screen
    Properties:
      OnVisible: |
        Set(varSelectedTab, "Übersicht"); Refresh('Urlaubsantraege')
    Children:
      galAntraege:
        Control: gallery
        Properties:
          Items: |
            SortByColumns(Filter('Urlaubsantraege', Mitarbeiter.Email = varCurrentUser.Mail), "VonDatum", Descending)
        Children:
          btnDetails:
            Control: button
            Properties:
              Text: Details
              OnSelect: |
                Set(varSelectedAntrag, ThisItem); Navigate(DetailScreen, ScreenTransition.Fade)
      btnNeuerAntrag:
        Control: button
        Properties:
          Text: "Neuer Antrag"
          OnSelect: Navigate(NeuerAntragScreen, ScreenTransition.Cover)
  NeuerAntragScreen:
    Control: screen
    Children:
      frmAntrag:
        Control: form
        Properties:
          DataSource: "'Urlaubsantraege'"
          DefaultMode: FormMode.New
          OnSuccess: |
            Notify("Eingereicht!", NotificationType.Success); Navigate(HomeScreen)
        Children:
          dcVonDatum:
            Control: datacard
            Properties: {DataField: VonDatum, Default: "Today()", Update: "dpVonDatum.SelectedDate"}
      btnSubmit:
        Control: button
        Properties:
          OnSelect: |
            If(IsBlank(dpVonDatum.SelectedDate), Notify("Pflichtfeld!", NotificationType.Warning), SubmitForm(frmAntrag))
  DetailScreen:
    Control: screen
    Children:
      btnGenehmigen:
        Control: button
        Properties:
          Visible: varCanApprove
          OnSelect: |
            Patch('Urlaubsantraege', varSelectedAntrag, {Status: "Genehmigt"}); Navigate(HomeScreen)
Connections:
  Office365Users: {type: Office365Users, connectionId: "shared-office365users-a1b2c3d4-e5f6-7890-abcd-ef1234567890"}"""

FRAGMENT_SAMPLE = r"""# Fragment-Beispiel: Einzelnes Kontrollelement
btnSubmit:
  Control: button
  Properties:
    Text: "Formular absenden"
    Fill: "RGBA(91, 127, 255, 1)"
    Color: "White"
    DisplayMode: |
      If(
        IsBlank(txtName.Text) || IsBlank(txtEmail.Text),
        DisplayMode.Disabled,
        DisplayMode.Edit
      )
    OnSelect: |
      If(
        IsBlank(txtName.Text),
        Notify("Name ist ein Pflichtfeld", NotificationType.Error),
        SubmitForm(frmKontakt);
        Notify("Erfolgreich gesendet!", NotificationType.Success);
        Navigate(HomeScreen, ScreenTransition.Fade)
      )"""

JS = r"""
let pg='yaml',sum=null,dif=null,parseMode='auto';
const pages=[['yaml','&#128229; Import'],['summary','&#128202; Übersicht'],['screenshots','&#128444; Screenshots'],['notes','&#128221; Notizen'],['generate','&#128196; Generieren'],['model','&#128300; Modell']];
function esc(s){if(!s)return'';return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function stat(v,l){return`<div class="st"><div class="sn">${v}</div><div class="sl">${l}</div></div>`}
function toast(m,tp){const e=document.createElement('div');e.className='tst';e.style.background=tp==='error'?'var(--err)':tp==='warn'?'var(--warn)':'var(--ok)';e.textContent=m;document.getElementById('tc').appendChild(e);setTimeout(()=>e.remove(),4000)}
function renderSb(){document.getElementById('sb').innerHTML=pages.map(([k,l])=>`<div class="si ${pg===k?'a':''}" onclick="nav('${k}')">${l}</div>`).join('')+`<div class="wf"><b>Workflow:</b><br>1. YAML/.msapp importieren<br>2. Übersicht prüfen<br>3. Screenshots (optional)<br>4. Notizen ergänzen<br>5. Generieren</div>`}
function nav(p){pg=p;renderSb();render()}
function render(){
  const ct=document.getElementById('ct');
  if(pg==='yaml'){ct.innerHTML=pgYaml();setupDrop()}
  else if(pg==='summary'){ct.innerHTML=pgSum()}
  else if(pg==='screenshots'){loadSS()}
  else if(pg==='notes'){loadNotes()}
  else if(pg==='generate'){ct.innerHTML=pgGen()}
  else if(pg==='model'){loadModel()}
}
function setMode(m){parseMode=m;document.querySelectorAll('.mode-opt').forEach(b=>b.classList.toggle('act',b.dataset.mode===m))}
// === YAML PAGE ===
function pgYaml(){
  return`<div class="cd"><div class="cdt">&#128229; YAML / .msapp importieren</div>
  <p style="color:var(--mut);font-size:13px;margin-bottom:12px">Vollständige App (YAML oder .msapp), einzelne Screens oder einzelne Kontrollelemente importieren.</p>
  <div style="margin-bottom:16px"><label class="lb">Eingabemodus</label>
    <div class="mode-sel">
      <button class="mode-opt ${parseMode==='auto'?'act':''}" data-mode="auto" onclick="setMode('auto')">&#9881; Auto-Erkennung</button>
      <button class="mode-opt ${parseMode==='full'?'act':''}" data-mode="full" onclick="setMode('full')">&#128196; Vollständige App</button>
      <button class="mode-opt ${parseMode==='fragment'?'act':''}" data-mode="fragment" onclick="setMode('fragment')">&#129513; Fragment</button>
    </div>
    <div style="font-size:11px;color:var(--mut);margin-top:6px">${parseMode==='auto'?'Erkennt automatisch ob vollständige App oder Fragment.':parseMode==='full'?'Erwartet eine vollständige App-Definition (YAML-Export oder .msapp).':'Einzelne Screens, Controls oder Formel-Blöcke. Werden automatisch eingebettet.'}</div>
  </div>
  <div class="dz" id="dz" onclick="document.getElementById('yf').click()">
    <div style="font-size:32px;margin-bottom:8px">&#128193;</div>
    <div>YAML- oder <b>.msapp</b>-Datei hier ablegen oder klicken</div>
    <div style="font-size:12px;margin-top:4px">(.yaml, .yml, .txt, <b>.msapp</b>)</div>
  </div>
  <input type="file" id="yf" accept=".yaml,.yml,.txt,.msapp" style="display:none" onchange="hFile(this)">
  <div class="dv"><div class="dv-l"></div><span style="color:var(--mut);font-size:12px">ODER YAML einfügen</span><div class="dv-l"></div></div>
  <textarea id="yt" class="inp ta" placeholder="YAML hier einfügen (vollständige App oder Fragment)..." spellcheck="false"></textarea>
  <div class="f g10 mt12 fw">
    <button class="btn bp" id="pb" onclick="doparse()">&#128269; Analysieren</button>
    <button class="btn bg" onclick="document.getElementById('yt').value=''">Leeren</button>
    <button class="btn bo" onclick="document.getElementById('yt').value=SAMPLE;setMode('auto');toast('Beispiel geladen')">&#128203; App-Beispiel</button>
    <button class="btn bo" onclick="document.getElementById('yt').value=FRAGMENT_SAMPLE;setMode('fragment');toast('Fragment-Beispiel geladen')">&#129513; Fragment-Beispiel</button>
  </div></div>`
}
function setupDrop(){const d=document.getElementById('dz');if(!d)return;d.ondragover=e=>{e.preventDefault();d.classList.add('ov')};d.ondragleave=()=>d.classList.remove('ov');d.ondrop=e=>{e.preventDefault();d.classList.remove('ov');if(e.dataTransfer.files[0])hF2(e.dataTransfer.files[0])}}
async function hFile(i){if(i.files[0])hF2(i.files[0])}
async function hF2(file){
  const fname=file.name.toLowerCase();
  if(fname.endsWith('.msapp')){
    // Upload as binary .msapp
    const fd=new FormData();fd.append('msapp_file',file);fd.append('mode',parseMode);
    const b=document.getElementById('pb');if(b){b.disabled=true;b.textContent='Wird analysiert...';}
    try{
      const r=await fetch('/api/parse',{method:'POST',body:fd});
      if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||'Fehler')}
      const d=await r.json();sum=d.summary;dif=d.diff;
      toast('MSAPP: '+d.summary.screen_count+' Bildschirme, '+d.summary.control_count+' Kontrollelemente');
      nav('summary');
    }catch(e){toast(e.message,'error')}
    finally{if(b){b.disabled=false;b.textContent='Analysieren';}}
  }else{
    const t=await file.text();document.getElementById('yt').value=t;doparse();
  }
}
async function doparse(){
  const t=document.getElementById('yt').value;
  if(!t.trim())return toast('Kein Inhalt.','error');
  const b=document.getElementById('pb');b.disabled=true;b.textContent='Wird analysiert...';
  try{
    const fd=new FormData();fd.append('yaml_text',t);fd.append('mode',parseMode);
    const r=await fetch('/api/parse',{method:'POST',body:fd});
    if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||'Fehler')}
    const d=await r.json();sum=d.summary;dif=d.diff;
    const modeInfo=d.summary.parse_mode==='fragment'?' (Fragment)':'';
    const srcInfo=d.summary.input_type==='msapp'?' [MSAPP]':'';
    toast('OK'+srcInfo+modeInfo+': '+d.summary.screen_count+' Screens, '+d.summary.control_count+' Controls');
    nav('summary');
  }catch(e){toast(e.message,'error')}
  finally{b.disabled=false;b.textContent='Analysieren'}
}
// === SUMMARY ===
function pgSum(){
  if(!sum)return`<div class="cd"><div style="color:var(--mut);text-align:center;padding:40px">Bitte YAML oder .msapp importieren.</div></div>`;
  const s=sum;
  let h='';
  // Mode/type banners
  if(s.input_type==='msapp')h+=`<div class="info-banner msapp">&#128230; Importiert aus <b>.msapp</b>-Datei</div>`;
  if(s.parse_mode==='fragment')h+=`<div class="info-banner frag">&#129513; <b>Fragment-Modus</b> — Teildokumentation aus YAML-Fragment</div>`;
  h+=`<div class="cd"><div class="cdt">&#128202; ${esc(s.app_name)}</div><div class="sts">${stat(s.screen_count,'Bildschirme')}${stat(s.control_count,'Kontrollelemente')}${stat(s.formula_count,'Formeln')}${stat(s.connector_count,'Konnektoren')}${stat(s.variable_count,'Variablen')}${stat(s.collection_count,'Sammlungen')}${stat(s.component_count,'Komponenten')}</div>`;
  // Badges
  h+=`<div class="f g6 mt12 fw">`;
  if(s.input_type==='msapp')h+=`<span class="badge b-msapp">MSAPP</span>`;
  if(s.parse_mode==='fragment')h+=`<span class="badge b-frag">Fragment</span>`;
  h+=`</div>`;
  if(s.unparsed_sections>0)h+=`<div class="mt12" style="padding:8px 14px;background:rgba(245,158,11,.08);border-radius:6px;color:var(--warn);font-size:13px">&#9888; ${s.unparsed_sections} nicht interpretiert.</div>`;
  h+=`</div>`;
  if(dif){
    h+=`<div class="cd"><div class="cdt">&#128260; Änderungen</div><p style="color:var(--mut);font-size:13px;margin-bottom:8px">${esc(dif.summary)}</p>`;
    if(dif.screens_added&&dif.screens_added.length)h+=`<div class="mb8"><span class="badge b-ok">+Neu</span> ${esc(dif.screens_added.join(', '))}</div>`;
    if(dif.screens_removed&&dif.screens_removed.length)h+=`<div class="mb8"><span class="badge b-er">-Entfernt</span> ${esc(dif.screens_removed.join(', '))}</div>`;
    if(dif.formula_changes&&dif.formula_changes.length)h+=`<div><span class="badge b-wa">~Geändert</span> ${dif.formula_changes.length} Formeländerung(en)</div>`;
    h+=`</div>`;
  }
  return h;
}
// === SCREENSHOTS ===
async function loadSS(){const ct=document.getElementById('ct');try{const[sr,ir,pr]=await Promise.all([fetch('/api/screens').then(r=>r.json()),fetch('/api/images').then(r=>r.json()),fetch('/api/project').then(r=>r.json())]);const screens=sr.screens||[],images=ir.images||[],map=pr.project?.screenshot_map||{};let h=`<div class="cd"><div class="cdt">&#128444; Screenshots</div><div class="f g10 mb16"><button class="btn bp" onclick="document.getElementById('sf').click()">Bilder hochladen</button><input type="file" id="sf" accept="image/*" multiple style="display:none" onchange="uploadSS(this)"><button class="btn bo" onclick="let i=document.createElement('input');i.type='file';i.accept='.zip';i.onchange=e=>uploadZip(e.target.files[0]);i.click()">ZIP</button></div>`;if(images.length)h+=`<div class="f g6 fw">${images.map(i=>`<div style="padding:4px 8px;background:var(--sfc2);border-radius:4px;font-size:12px;color:var(--mut)">${esc(i)}</div>`).join('')}</div>`;h+=`</div><div class="cd"><div class="cdt">&#128279; Zuordnung</div><div class="f g10 mb16"><button class="btn bo" onclick="autoMatch()">Auto</button><button class="btn bp" onclick="saveMap()">Speichern</button></div>`;if(!screens.length)h+=`<p style="color:var(--mut);font-size:13px">Keine Bildschirme.</p>`;else{h+=`<table><thead><tr><th>Bildschirm</th><th>Screenshot</th></tr></thead><tbody>`;for(const s of screens)h+=`<tr><td>${esc(s)}</td><td><select class="sel ssm" data-screen="${esc(s)}"><option value="">-</option>${images.map(i=>`<option value="${esc(i)}" ${map[s]===i?'selected':''}>${esc(i)}</option>`).join('')}</select>${map[s]?`<img src="/images/${encodeURIComponent(map[s])}" class="it">`:''}
</td></tr>`;h+=`</tbody></table>`}h+=`</div>`;ct.innerHTML=h}catch(e){toast(e.message,'error')}}
async function uploadSS(input){const fd=new FormData();for(const f of input.files)fd.append('files',f);try{await fetch('/api/screenshots/upload',{method:'POST',body:fd});toast('Hochgeladen');loadSS()}catch(e){toast(e.message,'error')}}
async function uploadZip(file){if(!file)return;const fd=new FormData();fd.append('file',file);try{await fetch('/api/screenshots/upload-zip',{method:'POST',body:fd});toast('ZIP hochgeladen');loadSS()}catch(e){toast(e.message,'error')}}
async function autoMatch(){try{const r=await fetch('/api/screenshots/auto-match').then(r=>r.json());if(Object.keys(r.matches).length){document.querySelectorAll('.ssm').forEach(sel=>{if(r.matches[sel.dataset.screen])sel.value=r.matches[sel.dataset.screen]});toast(Object.keys(r.matches).length+' Zuordnungen')}else toast('Keine gefunden','warn')}catch(e){toast(e.message,'error')}}
async function saveMap(){const map={};document.querySelectorAll('.ssm').forEach(sel=>{if(sel.value)map[sel.dataset.screen]=sel.value});try{await fetch('/api/screenshots/map',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(map)});toast('Gespeichert')}catch(e){toast(e.message,'error')}}
// === NOTES ===
const NF=[['purpose','Zweck / Geschäftskontext'],['intended_users','Zielbenutzer & Rollen'],['environments','Umgebungen (DEV/TEST/PROD)'],['roles','Rollenkonzept'],['limitations','Einschränkungen'],['alm_notes','ALM / Deployment'],['security_notes','Sicherheitshinweise'],['connector_classification','Konnektor-Klassifizierung']];
async function loadNotes(){const ct=document.getElementById('ct');try{const d=await fetch('/api/project').then(r=>r.json());const n=d.project?.manual_notes||{},st=d.project?.settings||{redact_ids:true,include_best_practice_checks:true};let h=`<div class="cd"><div class="cdt">&#128221; Notizen</div>`;for(const[k,l] of NF)h+=`<div style="margin-bottom:14px"><label class="lb">${l}</label><textarea class="inp tas nt" data-key="${k}">${esc(n[k]||'')}</textarea></div>`;h+=`</div><div class="cd"><div class="cdt">&#9881; Einstellungen</div><label class="chk"><input type="checkbox" id="chkR" ${st.redact_ids?'checked':''}> IDs redaktieren</label><label class="chk"><input type="checkbox" id="chkBP" ${st.include_best_practice_checks?'checked':''}> Best-Practice-Prüfungen</label><div class="mt16"><button class="btn bp" onclick="saveNotes()">&#128190; Speichern</button></div></div>`;ct.innerHTML=h}catch(e){toast(e.message,'error')}}
async function saveNotes(){const notes={};document.querySelectorAll('.nt').forEach(t=>{notes[t.dataset.key]=t.value});const settings={redact_ids:document.getElementById('chkR').checked,include_best_practice_checks:document.getElementById('chkBP').checked};try{await fetch('/api/project/notes',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(notes)});await fetch('/api/project/settings',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(settings)});toast('Gespeichert')}catch(e){toast(e.message,'error')}}
// === GENERATE ===
let genFiles=[],pvC=null,pvF='html';
function pgGen(){let h=`<div class="cd"><div class="cdt">&#128196; Generieren</div><div class="f g16 mb16 fw">`;for(const[k,l] of [['md','Markdown'],['html','HTML'],['json','JSON'],['latex','LaTeX']])h+=`<label class="chk"><input type="checkbox" class="fc" value="${k}" checked> ${l}</label>`;h+=`</div><button class="btn bp" id="gb" onclick="doGen()">&#128196; Generieren</button>`;if(genFiles.length){h+=`<div class="mt16"><div style="font-size:14px;font-weight:600;margin-bottom:8px;color:var(--ok)">&#10003; Dateien:</div><div class="f g6 fw">`;for(const f of genFiles)h+=`<a href="/api/download/${f}" download class="dl">&#11015; ${f}</a>`;h+=`</div></div>`}h+=`</div><div class="cd"><div class="f" style="align-items:center;justify-content:space-between;margin-bottom:12px"><div class="cdt" style="margin:0">&#128065; Vorschau</div><div class="f g6">`;for(const f of ['html','md','json','latex'])h+=`<button class="btn bg bs ${pvF===f?'bo':''}" onclick="loadPv('${f}')">${f.toUpperCase()}</button>`;h+=`</div></div>`;if(pvC){if(pvF==='html')h+=`<iframe id="pvFrame" class="ifr" srcdoc=""></iframe>`;else h+=`<pre class="pre">${esc(pvC)}</pre>`}else h+=`<div style="color:var(--mut);text-align:center;padding:40px">Bitte generieren.</div>`;h+=`</div>`;return h}
async function doGen(){const fmts=[];document.querySelectorAll('.fc').forEach(c=>{if(c.checked)fmts.push(c.value)});if(!fmts.length)return toast('Format wählen','error');const b=document.getElementById('gb');b.disabled=true;b.textContent='...';try{const r=await fetch('/api/generate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(fmts)});if(!r.ok){const e=await r.json().catch(()=>({}));throw new Error(e.detail||'Fehler')}const d=await r.json();genFiles=d.generated;toast(d.generated.length+' generiert');render()}catch(e){toast(e.message,'error')}finally{b.disabled=false;b.textContent='Generieren'}}
async function loadPv(fmt){pvF=fmt;try{const d=await fetch('/api/preview/'+fmt).then(r=>r.json());pvC=d.content;render();if(fmt==='html'){const fr=document.getElementById('pvFrame');if(fr)fr.srcdoc=pvC}}catch(e){toast(e.message,'error')}}
// === MODEL ===
async function loadModel(){const ct=document.getElementById('ct');try{const m=await fetch('/api/model').then(r=>{if(!r.ok)throw new Error('x');return r.json()});const secs=[['screens','Bildschirme'],['connectors','Konnektoren'],['data_sources','Datenquellen'],['variables','Variablen'],['components','Komponenten'],['forms','Formulare'],['navigation_graph','Navigation'],['error_handling','Fehlerbehandlung'],['best_practice_findings','Best Practices']];let h=`<div class="cd"><div class="cdt">&#128300; Modell-Explorer</div>`;if(m.parse_mode==='fragment')h+=`<div class="info-banner frag">&#129513; Fragment-Modus</div>`;if(m.input_type==='msapp')h+=`<div class="info-banner msapp">&#128230; MSAPP-Import</div>`;h+=`<div class="f g6 fw mb16">`;for(const[k,l] of secs)h+=`<button class="btn bg bs" onclick="showSec('${k}',this)">${l}</button>`;h+=`</div><div id="secC"></div></div>`;ct.innerHTML=h;window._m=m}catch(e){ct.innerHTML=`<div class="cd"><div style="color:var(--mut);text-align:center;padding:40px">Kein Modell.</div></div>`}}
function showSec(key,btn){document.querySelectorAll('.cd .btn.bg.bs').forEach(b=>b.classList.remove('bo'));if(btn)btn.classList.add('bo');const m=window._m;if(!m)return;const data=m[key],el=document.getElementById('secC');if(!data||!data.length&&typeof data!=='object'){el.innerHTML='<p style="color:var(--mut)">Keine Daten.</p>';return}if(key==='screens')el.innerHTML=m.screens.map(s=>`<div class="sc"><div style="font-weight:600;margin-bottom:6px">${esc(s.name)}</div><div style="font-size:12px;color:var(--mut)">${s.controls.length} Controls, ${s.formulas.length} Formeln</div></div>`).join('');else if(key==='variables'){const v=m.variables;let h=`<h4 style="color:var(--acc);margin-bottom:8px">Global (${v.global_vars.length})</h4>`;v.global_vars.forEach(x=>{h+=`<div style="margin-bottom:4px;font-size:13px"><code style="color:var(--code)">${esc(x.name)}</code> - ${esc(x.locations.slice(0,2).join(', '))}</div>`});h+=`<h4 style="color:var(--acc);margin:16px 0 8px">Kontext (${v.context_vars.length})</h4>`;v.context_vars.forEach(x=>{h+=`<div style="margin-bottom:4px;font-size:13px"><code style="color:var(--code)">${esc(x.name)}</code></div>`});h+=`<h4 style="color:var(--acc);margin:16px 0 8px">Sammlungen (${v.collections.length})</h4>`;v.collections.forEach(x=>{h+=`<div style="margin-bottom:4px;font-size:13px"><code style="color:var(--code)">${esc(x.name)}</code></div>`});el.innerHTML=h}else if(key==='best_practice_findings')el.innerHTML=m.best_practice_findings.map(f=>`<div class="fd ${f.severity==='warning'?'fd-w':'fd-i'}"><div style="font-weight:600;font-size:13px">${f.severity==='warning'?'&#9888;':'&#8505;'} [${esc(f.type)}]</div><div style="font-size:13px;margin-top:4px">${esc(f.message_de)}</div><div style="font-size:11px;color:var(--mut);margin-top:2px">${esc(f.location)}</div></div>`).join('');else if(Array.isArray(data))el.innerHTML=data.map(item=>`<div class="sc"><pre style="margin:0;white-space:pre-wrap;font-family:var(--mono);font-size:12px;color:var(--code)">${esc(JSON.stringify(item,null,2))}</pre></div>`).join('');else el.innerHTML=`<pre class="pre">${esc(JSON.stringify(data,null,2))}</pre>`}
// === RESET ===
async function doReset(){if(!confirm('Projekt zurücksetzen?'))return;try{await fetch('/api/reset',{method:'POST'});sum=null;dif=null;genFiles=[];pvC=null;nav('yaml');toast('Zurückgesetzt')}catch(e){toast(e.message,'error')}}
// === INIT ===
async function init(){renderSb();try{const d=await fetch('/api/project').then(r=>r.json());if(d.model_summary)sum=d.model_summary}catch(e){}render()}
init();
"""

# Assemble
html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Power Apps Doc Builder</title>
<style>{CSS}</style>
</head>
<body>
<div class="hdr">
  <div><div class="logo">&#9889; Power Apps Doc Builder</div><div class="logo-s">Canvas App Dokumentation &middot; YAML &amp; .msapp</div></div>
  <div style="flex:1"></div>
  <button class="btn bg bs" onclick="doReset()">&#128465; Zurücksetzen</button>
</div>
<div class="mn">
  <div class="sb" id="sb"></div>
  <div class="ct" id="ct"></div>
</div>
<div id="tc"></div>
<script>
const SAMPLE={SAMPLE!r};
const FRAGMENT_SAMPLE={FRAGMENT_SAMPLE!r};
{JS}
</script>
</body>
</html>"""

out = Path(__file__).parent.parent / "frontend" / "index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print(f"Generated: {out} ({len(html)} bytes)")
