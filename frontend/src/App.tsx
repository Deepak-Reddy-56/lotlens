import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from "react";
import { Activity, AlertTriangle, ArrowRight, BrainCircuit, Check, ClipboardCheck, Factory, FileSearch, Plus, RefreshCw, Search, ShieldCheck, Sparkles, X } from "lucide-react";
import { api, type ActionRecord, type CaseRecord, type Investigation } from "./api";

const emptyForm = {
  supplier_code: "SUP-C", supplier_name: "Supplier C",
  component_code: "BMS-CONN", component_name: "BMS Connector",
  lot_code: "C301", symptoms: "Intermittent open-circuit readings during vibration testing",
  description: "Newly reported connector failure during end-of-line validation.", severity: "high",
};
const statusClass = (value: string) => value.toLowerCase().replaceAll("_", "-");

export default function App() {
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [investigation, setInvestigation] = useState<Investigation | null>(null);
  const [actions, setActions] = useState<ActionRecord[]>([]);
  const [selectedActionId, setSelectedActionId] = useState("");
  const [health, setHealth] = useState<{status:string;hindsight_configured:boolean;bank_id:string}|null>(null);
  const [busy, setBusy] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [showNew, setShowNew] = useState(false);
  const [actionText, setActionText] = useState("");
  const [verifiedBy, setVerifiedBy] = useState("Quality Engineer");
  const [actionOutcome, setActionOutcome] = useState("effective");
  const [rootStatus, setRootStatus] = useState("unknown");
  const [rootCause, setRootCause] = useState("");
  const [form, setForm] = useState(emptyForm);
  const selected = useMemo(() => cases.find((item) => item.id === selectedId) ?? null, [cases, selectedId]);

  async function refresh() {
    setLoading(true); setError("");
    try {
      const [rows, status] = await Promise.all([api.listCases(), api.health()]);
      setCases(rows); setHealth(status);
      const nextId = selectedId && rows.some((row) => row.id === selectedId) ? selectedId : rows[0]?.id ?? null;
      setSelectedId(nextId);
      const nextActions = nextId ? rows.find((row) => row.id === nextId)?.actions ?? [] : [];
      setActions(nextActions);
      const preferredActionId = nextActions.some((action) => action.id === selectedActionId)
        ? selectedActionId
        : nextActions[nextActions.length - 1]?.id ?? "";
      setSelectedActionId(preferredActionId);
    } catch (e) { setError(e instanceof Error ? e.message : "Unable to load LotLens."); }
    finally { setLoading(false); }
  }
  useEffect(() => { void refresh(); }, []);

  async function seedDemo() {
    setBusy("seed"); setError(""); setNotice("");
    try { const result = await api.seedDemo(); setNotice(`Demo database ready. Added ${result.created} new records.`); await refresh(); }
    catch(e) { setError(e instanceof Error ? e.message : "Could not load demo data."); }
    finally { setBusy(""); }
  }

  async function createCase(e: FormEvent) {
    e.preventDefault(); setBusy("create"); setError(""); setNotice("");
    try {
      const created = await api.createCase(form);
      setNotice(`Created ${created.case_code}.`); setShowNew(false); setForm(emptyForm);
      await refresh(); setSelectedId(created.id); setActions([]); setSelectedActionId("");
    } catch(e) { setError(e instanceof Error ? e.message : "Could not create case."); }
    finally { setBusy(""); }
  }

  function selectCase(item: CaseRecord) {
    const nextActions = item.actions ?? [];
    setSelectedId(item.id); setActions(nextActions);
    setSelectedActionId(nextActions[nextActions.length - 1]?.id ?? "");
    setInvestigation(null); setActionText("");
  }

  async function investigate() {
    if (!selected) return;
    setBusy("investigate"); setError(""); setNotice(""); setInvestigation(null);
    try {
      const result = await api.investigate(selected.id);
      setInvestigation(result); setNotice("Investigation completed. Historical references were checked against canonical case records.");
      await refresh();
    } catch(e) { setError(e instanceof Error ? e.message : "Investigation failed."); }
    finally { setBusy(""); }
  }

  async function proposeAction(e: FormEvent) {
    e.preventDefault(); if (!selected || actionText.trim().length < 8) return;
    setBusy("action"); setError(""); setNotice("");
    try {
      const action = await api.createAction(selected.id, actionText);
      setActions((old) => [...old, action]); setSelectedActionId(action.id); setActionText(""); setNotice("Corrective action recorded and awaiting QA.");
      await refresh();
    } catch(e) { setError(e instanceof Error ? e.message : "Could not record corrective action."); }
    finally { setBusy(""); }
  }

  async function verifyAction(e: FormEvent) {
    e.preventDefault(); if (!selected || !selectedActionId) return;
    const action = actions.find((item) => item.id === selectedActionId);
    if (!action) { setError("Select a corrective action to verify."); return; }
    setBusy("verify"); setError(""); setNotice("");
    try {
      const result = await api.verify(selected.id, {
        action_id: action.id, action_outcome: actionOutcome, root_cause_status: rootStatus,
        confirmed_root_cause: rootStatus === "confirmed" ? rootCause : null,
        verified_by: verifiedBy, notes: "Verified through LotLens development dashboard.",
      });
      setNotice(`QA verification saved. Hindsight memory sync: ${result.memory_sync_status}.`);
      await refresh();
    } catch(e) { setError(e instanceof Error ? e.message : "QA verification failed."); }
    finally { setBusy(""); }
  }

  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-icon"><Activity size={19}/></div><div><b>lotlens</b><small>QUALITY INTELLIGENCE</small></div></div>
      <div className="side-label">WORKSPACE</div>
      <div className="side-link active"><Factory size={16}/> Investigations <span>{cases.length}</span></div>
      <button className="side-link" onClick={() => setShowNew(true)}><Plus size={16}/> New defect</button>
      <div className="side-bottom">
        <div className="connection"><i className={health?.hindsight_configured ? "online" : "offline"}/><div><b>Hindsight memory</b><small>{health?.hindsight_configured ? `Connected · ${health.bank_id}` : "Not configured"}</small></div></div>
        <div className="profile"><div className="avatar">QE</div><div><b>Quality Engineering</b><small>Development workspace</small></div></div>
      </div>
    </aside>

    <main className="main">
      <header className="topbar">
        <div><div className="eyebrow">MANUFACTURING / QUALITY OPERATIONS</div><h1>Investigation workspace</h1></div>
        <div className="top-buttons"><button className="icon-btn" onClick={() => void refresh()} title="Refresh"><RefreshCw size={16}/></button><button className="primary" onClick={() => setShowNew(true)}><Plus size={15}/> New defect</button></div>
      </header>
      <section className="metrics">
        <Metric icon={<FileSearch size={17}/>} label="Total investigations" value={cases.length} tone="blue" hint="Tracked production lots"/>
        <Metric icon={<AlertTriangle size={17}/>} label="Open investigations" value={cases.filter(c=>c.status!=="VERIFIED").length} tone="amber" hint="Need engineering attention"/>
        <Metric icon={<ShieldCheck size={17}/>} label="Verified outcomes" value={cases.filter(c=>c.status==="VERIFIED").length} tone="green" hint="QA-reviewed records"/>
        <Metric icon={<BrainCircuit size={17}/>} label="Memory layer" value={health?.hindsight_configured?"Online":"Offline"} tone="violet" hint={health?.bank_id ?? "Awaiting configuration"}/>
      </section>

      {error && <div className="notice error"><AlertTriangle size={15}/>{error}<button onClick={()=>setError("")}><X size={14}/></button></div>}
      {notice && <div className="notice success"><Check size={15}/>{notice}<button onClick={()=>setNotice("")}><X size={14}/></button></div>}

      <div className="columns">
        <section className="panel register">
          <div className="panel-head"><div><div className="eyebrow">CASE REGISTER</div><h2>Defect investigations</h2></div><button className="link-btn" disabled={busy==="seed"} onClick={()=>void seedDemo()}>{busy==="seed"?"Loading…":"Load demo data"}</button></div>
          <div className="searchbar"><Search size={14}/><span>Historical defect register</span><button onClick={()=>void refresh()}><RefreshCw size={13}/></button></div>
          <div className="case-list">
            {loading && <div className="empty">Loading cases…</div>}
            {!loading && cases.length===0 && <div className="empty"><FileSearch size={25}/><b>No investigations yet</b><span>Load the sample cases or report a defect.</span></div>}
            {cases.map(item=><button key={item.id} className={`case-row ${selectedId===item.id?"selected":""}`} onClick={()=>selectCase(item)}>
              <div className="case-row-head"><b>{item.case_code}</b><span className={`status ${statusClass(item.status)}`}>{item.status.replaceAll("_"," ")}</span></div>
              <strong>{item.symptoms}</strong><small>{item.supplier.name} · Lot {item.lot.code}</small>
            </button>)}
          </div>
        </section>

        <section className="detail-stack">
          {selected ? <>
            <section className="panel detail">
              <div className="panel-head"><div><div className="eyebrow">SELECTED INVESTIGATION</div><h2>{selected.case_code}</h2></div><span className={`status ${statusClass(selected.status)}`}>{selected.status.replaceAll("_"," ")}</span></div>
              <div className="facts">
                <div><small>SUPPLIER</small><b>{selected.supplier.name}</b><span>{selected.supplier.code}</span></div>
                <div><small>COMPONENT</small><b>{selected.component.name}</b><span>{selected.component.code}</span></div>
                <div><small>PRODUCTION LOT</small><b>{selected.lot.code}</b><span>{selected.severity.toUpperCase()} SEVERITY</span></div>
              </div>
              <div className="symptoms"><small>REPORTED SYMPTOMS</small><p>{selected.symptoms}</p><span>{selected.description}</span></div>
              <div className="root-status"><span>Root-cause status</span><b>{selected.root_cause_status}{selected.root_cause? ` · ${selected.root_cause}`:""}</b></div>
              <button className="primary full-width" disabled={busy==="investigate"||selected.status==="VERIFIED"} onClick={()=>void investigate()}><Sparkles size={15}/>{busy==="investigate"?"Investigating…":"Investigate with historical memory"}<ArrowRight size={15}/></button>
            </section>

            {investigation && <section className="panel intelligence">
              <div className="panel-head"><div><div className="eyebrow">HINDSIGHT SYNTHESIS</div><h2>Investigation intelligence</h2></div><span className="memory-chip"><BrainCircuit size={13}/> {investigation.memory_hit_count} hits</span></div>
              {investigation.evidence_cases.length>0 ? <div className="evidence"><small>CANONICAL HISTORICAL CASES</small>{investigation.evidence_cases.map(item=><div className="evidence-item" key={item.case_code}><div><b>{item.case_code}</b><span>{item.supplier_name} · {item.lot_code}</span></div><em>{item.root_cause_status}</em><p>{item.root_cause??"Root cause not confirmed"}</p></div>)}</div>:<div className="empty compact">No recalled case IDs matched canonical records. Treat unmatched memory as unlinked context.</div>}
              {investigation.unlinked_case_codes.length>0&&<div className="warning"><AlertTriangle size={13}/> Unlinked memory references: {investigation.unlinked_case_codes.join(", ")}</div>}
              {investigation.citation_warnings.length>0&&<div className="warning"><AlertTriangle size={13}/> Unvalidated case IDs mentioned in synthesis: {investigation.citation_warnings.join(", ")}</div>}
              <div className="narrative"><pre>{investigation.result_text}</pre></div>
              <div className="human-note"><ShieldCheck size={15}/> Human review required. Verify findings before taking action.</div>
            </section>}

            <section className="panel action-panel">
              <div className="panel-head"><div><div className="eyebrow">HUMAN-IN-THE-LOOP</div><h2>Corrective action & QA</h2></div><ClipboardCheck size={18}/></div>
              {actions.length>0&&<div className="existing-actions">{actions.map(a=><div key={a.id}><span>{a.description}</span><em>{a.outcome}</em></div>)}</div>}
              <form className="form-stack" onSubmit={proposeAction}>
                <label>Proposed corrective action<textarea required minLength={8} value={actionText} onChange={e=>setActionText(e.target.value)} placeholder="Describe the engineer-approved action to evaluate…"/></label>
                <button className="secondary" disabled={busy==="action"||selected.status==="VERIFIED"||!actionText.trim()}>{busy==="action"?"Saving…":"Record corrective action"}</button>
              </form>
              {actions.length>0&&selected.status!=="VERIFIED"&&<form className="verify-form" onSubmit={verifyAction}>
                <div className="divider-label">QA VERIFICATION</div>
                <label className="wide-field">Action to verify<select required value={selectedActionId} onChange={e=>setSelectedActionId(e.target.value)}>{actions.map(action=><option key={action.id} value={action.id}>{action.description} · {action.outcome}</option>)}</select></label>
                <label>Action outcome<select value={actionOutcome} onChange={e=>setActionOutcome(e.target.value)}><option value="effective">Effective</option><option value="ineffective">Ineffective</option><option value="inconclusive">Inconclusive</option></select></label>
                <label>Root-cause status<select value={rootStatus} onChange={e=>setRootStatus(e.target.value)}><option value="unknown">Unknown</option><option value="suspected">Suspected</option><option value="confirmed">Confirmed</option><option value="disputed">Disputed</option></select></label>
                {rootStatus==="confirmed"&&<label className="wide-field">Confirmed root cause<input required value={rootCause} onChange={e=>setRootCause(e.target.value)} placeholder="QA-confirmed cause"/></label>}
                <label className="wide-field">Verified by<input required value={verifiedBy} onChange={e=>setVerifiedBy(e.target.value)}/></label>
                <button className="primary wide-field" disabled={busy==="verify"}>{busy==="verify"?"Saving verification…":"Submit QA verification"}</button>
              </form>}
            </section>
          </>:<section className="panel empty detail-empty"><FileSearch size={28}/><b>Select an investigation</b><span>Choose a case or create a new defect.</span></section>}
        </section>
      </div>
      <footer><span>LOTLENS · DEVELOPMENT BUILD 0.1</span><span><Activity size={11}/> Database is canonical · Hindsight supplies persistent memory</span></footer>
    </main>

    {showNew&&<div className="modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setShowNew(false);}}><form className="modal" onSubmit={createCase}>
      <div className="panel-head"><div><div className="eyebrow">NEW QUALITY EVENT</div><h2>Report a defect</h2></div><button type="button" className="icon-btn" onClick={()=>setShowNew(false)}><X size={16}/></button></div>
      <div className="form-grid">
        {(["supplier_code","supplier_name","component_code","component_name","lot_code"] as const).map(key=><label key={key}>{key.replaceAll("_"," ")}<input required value={form[key]} onChange={e=>setForm({...form,[key]:e.target.value})}/></label>)}
        <label>Severity<select value={form.severity} onChange={e=>setForm({...form,severity:e.target.value})}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></label>
        <label className="wide-field">Reported symptoms<textarea required minLength={8} value={form.symptoms} onChange={e=>setForm({...form,symptoms:e.target.value})}/></label>
        <label className="wide-field">Additional description<textarea value={form.description} onChange={e=>setForm({...form,description:e.target.value})}/></label>
      </div>
      <div className="modal-actions"><button type="button" className="secondary" onClick={()=>setShowNew(false)}>Cancel</button><button className="primary" disabled={busy==="create"}>{busy==="create"?"Creating…":"Create defect case"}</button></div>
    </form></div>}
  </div>;
}

function Metric({icon,label,value,tone,hint}:{icon:ReactNode;label:string;value:string|number;tone:string;hint:string}) {
  return <div className="metric"><div className={`metric-icon ${tone}`}>{icon}</div><span>{label}</span><b>{value}</b><small>{hint}</small></div>;
}
