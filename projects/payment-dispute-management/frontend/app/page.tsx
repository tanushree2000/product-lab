"use client";
import { useEffect, useMemo, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type Dispute = {
 id:number; customer:string; merchant:string; amount:number; currency:string; reason:string; status:string;
 transaction_age_days:number; has_receipt:boolean; has_delivery_proof:boolean; customer_contacted:boolean;
 prior_successful_transactions:number; created_at:string;
};
type Decision = {recommendation:string;confidence:number;evidence_score:number;missing_evidence:string[];rationale:string[];human_review:boolean;analyst_summary:string};
type Metrics = {total_cases:number;open_cases:number;resolved_cases:number;human_review_cases:number;open_exposure:number};

const badge=(status:string)=> {
 const map:Record<string,string>={open:"bg-blue-50 text-blue-700",review:"bg-amber-50 text-amber-700",resolved:"bg-emerald-50 text-emerald-700",contested:"bg-violet-50 text-violet-700",accepted:"bg-slate-100 text-slate-700"};
 return map[status]||"bg-slate-100 text-slate-700";
};

export default function Home(){
 const [items,setItems]=useState<Dispute[]>([]);
 const [metrics,setMetrics]=useState<Metrics|null>(null);
 const [selected,setSelected]=useState<Dispute|null>(null);
 const [decision,setDecision]=useState<Decision|null>(null);
 const [q,setQ]=useState("");
 const [status,setStatus]=useState("all");
 const [loading,setLoading]=useState(true);

 async function refresh(){
   const [d,m]=await Promise.all([fetch(`${API}/api/disputes`).then(r=>r.json()),fetch(`${API}/api/metrics`).then(r=>r.json())]);
   setItems(d);setMetrics(m);setLoading(false);
 }
 useEffect(()=>{refresh().catch(()=>setLoading(false))},[]);

 const filtered=useMemo(()=>items.filter(d=>{
   const s=(d.customer+" "+d.merchant+" "+d.reason).toLowerCase();
   return s.includes(q.toLowerCase()) && (status==="all"||d.status===status);
 }),[items,q,status]);

 async function selectCase(d:Dispute){
   setSelected(d);setDecision(null);
   const x=await fetch(`${API}/api/disputes/${d.id}/analyze`,{method:"POST"}).then(r=>r.json());
   setDecision(x);
 }
 async function updateStatus(next:string){
   if(!selected)return;
   const d=await fetch(`${API}/api/disputes/${selected.id}/status`,{
     method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({status:next})
   }).then(r=>r.json());
   setSelected(d);await refresh();
 }

 return <div className="min-h-screen">
   <header className="border-b border-slate-200 bg-white">
    <div className="mx-auto max-w-7xl px-6 py-5">
      <h1 className="text-xl font-semibold">Payment Dispute Management System</h1>
      <p className="mt-1 text-sm text-slate-500">Operations dashboard · synthetic portfolio data · <a className="underline" href={`${API}/api/evaluation`} target="_blank">evaluation benchmark</a></p>
    </div>
   </header>

   <main className="mx-auto max-w-7xl px-6 py-8">
    <div className="grid gap-4 md:grid-cols-4">
      {[
        ["Total cases",metrics?.total_cases??"—"],
        ["Open cases",metrics?.open_cases??"—"],
        ["Human review",metrics?.human_review_cases??"—"],
        ["Open exposure",metrics?`$${metrics.open_exposure.toLocaleString()}`:"—"]
      ].map(([k,v])=><div key={k} className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <div className="text-sm text-slate-500">{k}</div><div className="mt-2 text-2xl font-semibold">{v}</div>
      </div>)}
    </div>

    <div className="mt-6 grid gap-6 lg:grid-cols-[1.35fr_.65fr]">
      <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-3 border-b border-slate-200 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div><h2 className="font-semibold">Dispute queue</h2><p className="text-sm text-slate-500">{filtered.length} cases</p></div>
          <div className="flex gap-2">
            <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search cases" className="w-44 rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500"/>
            <select value={status} onChange={e=>setStatus(e.target.value)} className="rounded-lg border border-slate-300 px-3 py-2 text-sm">
              <option value="all">All status</option><option value="open">Open</option><option value="review">Review</option><option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500"><tr>
              <th className="px-5 py-3">Case</th><th className="px-5 py-3">Merchant</th><th className="px-5 py-3">Reason</th><th className="px-5 py-3">Amount</th><th className="px-5 py-3">Status</th>
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
             {loading?<tr><td className="px-5 py-8 text-slate-500" colSpan={5}>Loading…</td></tr>:
             filtered.map(d=><tr key={d.id} onClick={()=>selectCase(d)} className="cursor-pointer hover:bg-slate-50">
               <td className="px-5 py-4 font-medium">#{d.id}<div className="font-normal text-slate-500">{d.customer}</div></td>
               <td className="px-5 py-4">{d.merchant}</td><td className="max-w-48 truncate px-5 py-4 text-slate-600">{d.reason}</td>
               <td className="px-5 py-4">${d.amount.toFixed(2)}</td>
               <td className="px-5 py-4"><span className={`rounded-full px-2.5 py-1 text-xs font-medium ${badge(d.status)}`}>{d.status}</span></td>
             </tr>)}
            </tbody>
          </table>
        </div>
      </section>

      <aside className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        {!selected?<div className="flex min-h-96 items-center justify-center text-center text-sm text-slate-500">Select a dispute to view the case analysis.</div>:
        <div>
          <div className="flex items-start justify-between gap-4"><div><div className="text-xs font-medium uppercase tracking-wide text-slate-500">Case #{selected.id}</div><h2 className="mt-1 text-lg font-semibold">{selected.merchant}</h2></div><span className={`rounded-full px-2.5 py-1 text-xs font-medium ${badge(selected.status)}`}>{selected.status}</span></div>
          <div className="mt-5 rounded-lg bg-slate-50 p-4"><div className="text-sm text-slate-500">Disputed amount</div><div className="mt-1 text-2xl font-semibold">${selected.amount.toFixed(2)}</div><div className="mt-2 text-sm">{selected.reason}</div></div>
          {!decision?<div className="py-8 text-sm text-slate-500">Analyzing evidence…</div>:<>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-lg border p-3"><div className="text-xs text-slate-500">Recommendation</div><div className="mt-1 font-semibold">{decision.recommendation.replace("_"," ")}</div></div>
              <div className="rounded-lg border p-3"><div className="text-xs text-slate-500">Evidence score</div><div className="mt-1 font-semibold">{decision.evidence_score}/100</div></div>
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-600">{decision.analyst_summary}</p>
            <h3 className="mt-5 text-sm font-semibold">Rationale</h3><ul className="mt-2 space-y-2 text-sm text-slate-600">{decision.rationale.map(x=><li key={x}>• {x}</li>)}</ul>
            <h3 className="mt-5 text-sm font-semibold">Missing evidence</h3><ul className="mt-2 space-y-2 text-sm text-slate-600">{decision.missing_evidence.length?decision.missing_evidence.map(x=><li key={x}>• {x}</li>):<li>None identified</li>}</ul>
            <div className="mt-6 flex flex-wrap gap-2">
              <button onClick={()=>updateStatus("review")} className="rounded-lg border border-slate-300 px-3 py-2 text-sm font-medium hover:bg-slate-50">Send to review</button>
              <button onClick={()=>updateStatus("resolved")} className="rounded-lg bg-slate-900 px-3 py-2 text-sm font-medium text-white hover:bg-slate-700">Mark resolved</button>
            </div>
          </>}
        </div>}
      </aside>
    </div>
   </main>
 </div>
}
