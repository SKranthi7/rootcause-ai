import React, {useState} from "react";
import {createRoot} from "react-dom/client";
import "./style.css";

function App(){
  const [repo,setRepo]=useState(null),[log,setLog]=useState(null),[trace,setTrace]=useState(null);
  const [result,setResult]=useState(null),[loading,setLoading]=useState(false);

  async function analyze(){
    if(!repo||!log||!trace) return alert("Upload repository, log and stack trace.");
    const f=new FormData(); f.append("repository",repo); f.append("log_file",log); f.append("stacktrace_file",trace);
    setLoading(true);
    try{
      const r=await fetch("http://localhost:8000/api/analyze",{method:"POST",body:f});
      const d=await r.json(); if(!r.ok) throw Error(d.detail||"Analysis failed"); setResult(d);
    }catch(e){alert(e.message)} finally{setLoading(false)}
  }

  return <div className="app">
    <header><div><h1>RootCause AI</h1><p>Production Incident Investigator</p></div><span className="badge">DEVELOPER TOOL</span></header>
    {!result?<section className="panel upload"><h2>Investigate an incident</h2>
      <p className="muted">Upload a Git repository, production log and stack trace.</p>
      <label>Git repository (.zip)<input type="file" accept=".zip" onChange={e=>setRepo(e.target.files[0])}/></label>
      <label>Application log<input type="file" accept=".log,.txt" onChange={e=>setLog(e.target.files[0])}/></label>
      <label>Stack trace<input type="file" accept=".txt,.log" onChange={e=>setTrace(e.target.files[0])}/></label>
      <button onClick={analyze} disabled={loading}>{loading?"Analyzing incident...":"Analyze Incident"}</button>
    </section>
    :<main>
      <section className="hero panel"><div><span className="severity">{result.incident.severity}</span>
        <h2>{result.incident.root_cause}</h2><p className="muted">{result.incident.affected_file}:{result.incident.affected_line}</p></div>
        <div className="confidence"><strong>{Math.round(result.incident.confidence*100)}%</strong><span>confidence</span></div></section>
      <section className="grid"><div className="panel"><h3>Evidence</h3>{result.evidence.signals.map((x,i)=><div className="item" key={i}>✓ {x}</div>)}</div>
        <div className="panel"><h3>Suspected Commit</h3><div className="commit">{result.incident.suspected_commit||"No match"}</div>
          {result.evidence.recent_changes?.map((x,i)=><p key={i}>{x.message}</p>)}</div></section>
      <section className="panel"><h3>Incident Timeline</h3>{result.timeline.map((x,i)=><div className="timeline" key={i}><b>{x.timestamp}</b><span>{x.type}</span><p>{x.description}</p></div>)}</section>
      <section className="grid"><div className="panel"><h3>Reasoning</h3>{result.reasoning.map((x,i)=><div className="item" key={i}>{i+1}. {x}</div>)}</div>
        <div className="panel"><h3>Recommended Actions</h3>{result.recommended_actions.map((x,i)=><div className="item" key={i}>→ {x}</div>)}</div></section>
      <section className="panel"><h3>Code Context</h3><pre>{result.evidence.code_context?.code||"No source context found."}</pre></section>
      <button className="secondary" onClick={()=>setResult(null)}>Analyze another incident</button>
    </main>}
  </div>
}
createRoot(document.getElementById("root")).render(<App/>);
