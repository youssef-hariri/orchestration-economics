"""Audit-only diagnostics. Reads original data; never imports/runs source mains.
Run with PYTHONDONTWRITEBYTECODE=1. All outputs remain beside this helper.
Student-t diagnostics are NOT substituted confirmatory analyses.
"""
from pathlib import Path
from collections import defaultdict, Counter
import csv, json, math, hashlib
import numpy as np
from scipy import stats
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
DIMS = ['Novelty','Usefulness','Flexibility','Elaboration','Cultural Sensitivity']
COLS = ['novelty','usefulness','flexibility','elaboration','cultural_sensitivity']
FAMS = ['claude','gemini','gpt','kimi','qwen']
def jl(path):
    return [json.loads(s) for s in (ROOT/path).read_text().splitlines() if s.strip()]
def dump(x):
    return json.dumps(x,indent=2,default=lambda v: v.item() if hasattr(v,'item') else str(v),allow_nan=False)
def judgments(path):
    raw=jl(path); per={}; allkeys=set(); bad=[]
    for i,j in enumerate(raw,1):
        k=(str(j['runId']),j['judge_family'],j['variant']); allkeys.add(k)
        if j.get('error') or j.get('incomplete'):
            bad.append({'line':i,'key':k,'error':j.get('error'),'incomplete':j.get('incomplete')}); continue
        per[k]=j['scores']
    acc=defaultdict(list)
    for (rid,jf,var),s in per.items(): acc[rid].append([s[d] for d in DIMS])
    sol={r:np.mean(a,axis=0) for r,a in acc.items()}
    info={'raw_rows':len(raw),'unique_all':len(allkeys),'unique_valid':len(per),'runs_valid':len(sol),
          'valid_counts_per_solution':dict(Counter(len(v) for v in acc.values())),
          'judges':dict(Counter(k[1] for k in per)), 'variants':dict(Counter(k[2] for k in per)),
          'models':sorted({j.get('judge_model','') for j in raw}),'bad_rows':bad,
          'missing_unique':sorted(allkeys-set(per)), 'first_ts':min(j.get('ts','') for j in raw),
          'last_ts':max(j.get('ts','') for j in raw)}
    return sol,info

def holm(p):
    order=np.argsort(p); adj=np.empty(len(p)); running=0
    for rank,i in enumerate(order):
        running=max(running,min(1,(len(p)-rank)*p[i])); adj[i]=running
    return adj.tolist()
def test(a,b):
    a=np.asarray(a); b=np.asarray(b); n=len(a); m=len(b)
    va=a.var(ddof=1); vb=b.var(ddof=1)
    sp=math.sqrt(((n-1)*va+(m-1)*vb)/(n+m-2)); diff=float(a.mean()-b.mean()); d=diff/sp
    tw=diff/math.sqrt(va/n+vb/m)
    dfw=(va/n+vb/m)**2/((va/n)**2/(n-1)+(vb/m)**2/(m-1))
    sed=math.sqrt((n+m)/(n*m)+d*d/(2*(n+m-2)))
    r={'n_arm':n,'n_base':m,'mean_arm':float(a.mean()),'mean_base':float(b.mean()),'diff':diff,
       'sd_arm':math.sqrt(va),'sd_base':math.sqrt(vb),'d_pooled':d,'welch_t':tw,'welch_df':dfw,
       'p_normal_two':float(2*stats.norm.sf(abs(tw))), 'p_welch_two':float(2*stats.t.sf(abs(tw),dfw)),
       'p_welch_pos':float(stats.t.sf(tw,dfw)), 'p_welch_neg':float(stats.t.cdf(tw,dfw)),
       'normal_d_ci90':[d-1.645*sed,d+1.645*sed]}
    if n==m:
        dif=a-b; sd=dif.std(ddof=1); tp=float(dif.mean()/(sd/math.sqrt(n)))
        r.update({'paired_t':tp,'paired_df':n-1,'sd_diff':float(sd),'d_z':float(dif.mean()/sd),
                  'p_paired_two':float(2*stats.t.sf(abs(tp),n-1)), 'p_paired_pos':float(stats.t.sf(tp,n-1)),
                  'p_paired_neg':float(stats.t.cdf(tp,n-1)), 'correlation':float(np.corrcoef(a,b)[0,1]),
                  'paired_diff_ci95':[float(dif.mean()-stats.t.ppf(.975,n-1)*sd/math.sqrt(n)),float(dif.mean()+stats.t.ppf(.975,n-1)*sd/math.sqrt(n))]})
    return r

def cells(sol):
    acc=defaultdict(list)
    for rid,s in sol.items():
        arm,f,p,rep=rid.split('__'); acc[(f,p,arm)].append(s)
    return {k:np.mean(v,axis=0) for k,v in acc.items()}
def value(s,dim): return float(s.mean()) if dim=='Composite' else float(s[DIMS.index(dim)])
def flow(path):
    raw=jl(path); latest={r['key']:r for r in raw}; counts={}; models={}
    for f in FAMS:
        for arm in ['D-SELF','D-FRONT']:
            records=[r for r in latest.values() if r['family']==f and r['arm']==arm]
            if records:
                counts[f+' '+arm]=dict(Counter(r['status'] for r in records))
                models[f+' '+arm]={'designer':sorted({r.get('designer_model','missing') for r in records}),
                                  'executor':sorted({r.get('executor_model','missing') for r in records})}
    info={'raw_rows':len(raw),'unique_keys':len(latest),'latest_counts':counts,'models':models,
          'all_statuses':dict(Counter(r['status'] for r in raw)),
          'first_started':min(r.get('started_at','') for r in raw),
          'terminal_failures':[{'line':max(i for i,x in enumerate(raw,1) if x['key']==r['key']),
             'key':r['key'],'status':r['status'],'error':r.get('error'),
             'has_designer_usage':bool(r.get('designer_usage')),'has_repair_usage':bool(r.get('designer_usage_repair'))}
             for r in latest.values() if r['status']!='completed']}
    return raw,latest,info

s3,ji=judgments('runs/study3/study3_judgments_v2.jsonl'); ca=cells(s3)
conf,cji=judgments('runs/study3conf/study3conf_judgments.jsonl'); cc=cells(conf)
raw,latest,fi=flow('runs/logs/study3_ledger_v2.jsonl')
cr,cl,cfi=flow('runs/logs/study3conf_ledger.jsonl')
res={'formulas':{'pairing':'Last valid judgment per (runId,judge_family,variant); mean judgments within solution; mean available rep solutions within family/problem/arm; match identical problem IDs. n=19 Study3; n=30 Protocol16.',
     'paired_t':'mean(a-b)/(sd(a-b,ddof=1)/sqrt(n)); two-sided p=2*scipy.stats.t.sf(abs(t),n-1), no prior rounding; Holm stepdown separately across five families for each DV.',
     'effect':'d_pooled=(mean(a)-mean(b))/sqrt(((n-1)*var(a)+(m-1)*var(b))/(n+m-2)); paired d_z separately = mean(a-b)/sd(a-b). Do not confuse these.',
     'welch':'t=diff/sqrt(va/n+vb/m); Welch-Satterthwaite df; actual Student t tails. With equal n the statistic equals d_pooled*sqrt(n/2), but a normal tail is not a Welch t distribution.',
     'ci':'Frozen Protocol16 CI = d +/- 1.645*sqrt((n+m)/(n*m)+d^2/(2*(n+m-2))); an unpaired normal approximation, not a paired TOST calculation.',
     'role':'All new tests audit-only diagnostics, not registered confirmatory results.'},
     'study3_judgments':ji,'study3_flow':fi,'protocol16_judgments':cji,'protocol16_flow':cfi}
res['authorship']={}
for dim in ['Novelty','Composite']:
    rows=[]
    for f in FAMS:
        ps=sorted({p for ff,p,a in ca if ff==f and (ff,p,'D-FRONT') in ca and (ff,p,'D-SELF') in ca})
        a=[value(ca[f,p,'D-FRONT'],dim) for p in ps]; b=[value(ca[f,p,'D-SELF'],dim) for p in ps]
        r={'family':f,'problem_ids':ps,**test(a,b)}
        r['frozen_rounded_t_normal_p']=float(2*stats.norm.sf(abs(round(r['paired_t'],3))))
        rows.append(r)
    for r,h,h0 in zip(rows,holm([r['p_paired_two'] for r in rows]),holm([r['frozen_rounded_t_normal_p'] for r in rows])):
        r['student_p_holm']=h; r['frozen_normal_p_holm']=h0
    res['authorship'][dim]=rows
res['pooled_authorship']={arm:{d:float(np.mean([value(v,d) for (f,p,a),v in ca.items() if a==arm])) for d in DIMS+['Composite']} for arm in ['D-SELF','D-FRONT']}
# Full Study1 long aggregate: verify each value against raw main judgments and metadata.
base_rows=list(csv.DictReader((ROOT/'evaluation/scores_aggregated.csv').open()))
main,maininfo=judgments('runs/logs/main_judgments.jsonl')
ml=json.loads((ROOT/'runs/logs/main_run_ledger.json').read_text())['results']
meta={str(r['runId']):r for r in ml if r.get('status')=='completed'}
bs=defaultdict(list); bp=defaultdict(list)
for r in base_rows:
    arr=np.array([float(r[c]) for c in COLS]); key=(r['family'],r['problem_id'],r['cell'])
    bp[key].append(arr); bs[(r['family'],r['problem_id'],r['cell'],r['run_id'])].append(arr)
bp={k:np.mean(v,axis=0) for k,v in bp.items()}; bs={k:np.mean(v,axis=0) for k,v in bs.items()}
res['baseline_validation']={'solutions':len(bs),'max_abs_solution_difference_from_raw':max(float(np.max(np.abs(v-main[k[3]]))) for k,v in bs.items() if k[3] in main),
 'missing_raw_run_ids':[k[3] for k in bs if k[3] not in main], 'ctn_solution_counts':dict(Counter(k[0] for k in bs if k[2]=='C-T-N')),
 'fsn_solution_counts':dict(Counter(k[0] for k in bs if k[2]=='F-S-N'))}
res['contrast_B']={}; res['vs_fsn_paired']={}; res['vs_fsn_solution_level']=[]
for dim in ['Novelty','Composite']:
    rb=[]; rf=[]
    for f in FAMS:
        for arm in ['D-SELF','D-FRONT']:
            ps=sorted(p for ff,p,a in ca if ff==f and a==arm)
            a=[value(ca[f,p,arm],dim) for p in ps]
            rb.append({'family':f,'arm':arm,**test(a,[value(bp[f,p,'C-T-N'],dim) for p in ps])})
            rf.append({'family':f,'arm':arm,**test(a,[value(bp[f,p,'F-S-N'],dim) for p in ps])})
    for rows in [rb,rf]:
        for r,h in zip(rows,holm([r['p_paired_two'] for r in rows])): r['paired_holm_10_diagnostic']=h
    res['contrast_B'][dim]=rb; res['vs_fsn_paired'][dim]=rf
for f in FAMS:
    for dim in DIMS+['Composite']:
        for arm in ['D-SELF','D-FRONT']:
            a=[value(s,dim) for rid,s in s3.items() if rid.split('__')[:2]==[arm,f]]
            b=[value(s,dim) for (ff,p,c,rid),s in bs.items() if ff==f and c=='F-S-N']
            res['vs_fsn_solution_level'].append({'family':f,'dimension':dim,'arm':arm,**test(a,b)})
vr=[r for r in res['vs_fsn_solution_level'] if r['dimension']!='Composite']
for r,h in zip(vr,holm([r['p_normal_two'] for r in vr])): r['normal_holm50']=h
for r,h in zip(vr,holm([r['p_welch_two'] for r in vr])): r['student_welch_holm50']=h
res['pooled_vs_fsn']={}
for arm in ['D-SELF','D-FRONT']:
    res['pooled_vs_fsn'][arm]=test([s[0] for rid,s in s3.items() if rid.startswith(arm+'__')],[s[0] for (f,p,c,rid),s in bs.items() if c=='F-S-N'])
# Protocol16 raw wave comparator, same problems, Novelty and composite.
w,wji=judgments('runs/logs/wave_judgments.jsonl')
wl=json.loads((ROOT/'runs/logs/wave_run_ledger.json').read_text())['results']
wm={str(r['runId']):r for r in wl if r.get('status')=='completed' and r.get('cell')=='F-S-N'}
wa=defaultdict(list)
for rid,r in wm.items():
    if rid in w: wa[(r['family'],r['problemId'])].append(w[rid])
wp={k:np.mean(v,axis=0) for k,v in wa.items()}
res['protocol16_comparator']={f:{'completed_runs':sum(r['family']==f for r in wm.values()),'judged_runs':sum(len(v) for (ff,p),v in wa.items() if ff==f),'problems':sum(ff==f for ff,p in wp)} for f in FAMS}
res['protocol16_tests']={}
for dim in ['Novelty','Composite']:
    rows=[]
    for f in FAMS:
        ps=sorted(p for ff,p,a in cc if ff==f and (f,p) in wp)
        rows.append({'family':f,'problem_ids':ps,**test([value(cc[f,p,'D-SELF'],dim) for p in ps],[value(wp[f,p],dim) for p in ps])})
    res['protocol16_tests'][dim]=rows
res['protocol16_hash']=hashlib.sha256((ROOT/'code/study3conf_analysis.py').read_bytes()).hexdigest()
res['problem_overlap']=sorted({p for f,p,a in ca}&{p for f,p,a in cc})
# Cost: reproduce frozen estimator, then latest-completed + repairs; do not call it total campaign cost.
prices=json.loads((ROOT/'config/price_vector.json').read_text())['prices']
reg=json.loads((ROOT/'config/model_registry.json').read_text())['generators']
def cost_usage(u,model):
    u=u or {}; p=prices[{'moonshotai/Kimi-K3':'kimi-k3'}.get(model,model)]
    return ((u.get('input_tokens',u.get('prompt_tokens',0)) or 0)*p['input']+(u.get('output_tokens',u.get('completion_tokens',0)) or 0)*p['output'])/1e6
def cost_r(r,repair=False):
    dm=r.get('designer_model')
    if not dm: return 0.
    v=cost_usage(r.get('designer_usage'),dm)
    if repair: v+=cost_usage(r.get('designer_usage_repair'),dm)
    xm=r.get('executor_model',reg[r['family']]['cheap_sibling']['model'])
    return v+sum(cost_usage(s.get('usage'),xm) for s in r.get('steps',[]))
def tokens(u,normalize=False):
    u=u or {}
    return (u.get('total_tokens',0) if not normalize else (u.get('input_tokens',u.get('prompt_tokens',0)) or 0)+(u.get('output_tokens',u.get('completion_tokens',0)) or 0))
res['costs']=[]
for f in FAMS:
    fs=[r for r in ml if r.get('status')=='completed' and r.get('cell')=='F-S-N' and r['family']==f]
    p=prices[reg[f]['frontier']['model']]
    fcost=float(np.mean([r['totalTokensUsed']*(.15*p['input']+.85*p['output'])/1e6 for r in fs]))
    for arm in ['D-SELF','D-FRONT']:
        rs=[r for r in raw if r['family']==f and r['arm']==arm and r['status']=='completed']
        ls=[r for r in latest.values() if r['family']==f and r['arm']==arm and r['status']=='completed']
        fail=[r for r in raw if r['family']==f and r['arm']==arm and r['status']!='completed']
        c=float(np.mean([cost_r(r) for r in rs])); lc=float(np.mean([cost_r(r,True) for r in ls]))
        res['costs'].append({'family':f,'arm':arm,'fsn_n':len(fs),'fsn_approx_cost':fcost,'frozen_n_records':len(rs),
           'latest_completed_n':len(ls),'frozen_mean_cost':c,'frozen_ratio':c/fcost,
           'latest_completed_with_repair_mean_cost':lc,'latest_completed_with_repair_ratio':lc/fcost,
           'repair_cost_completed_records':sum(cost_usage(r.get('designer_usage_repair'),r['designer_model']) for r in rs),
           'recorded_noncompleted_cost_not_deduped':sum(cost_r(r,True) for r in fail),
           'latest_completed_missing_designer_usage':sum(not r.get('designer_usage') for r in ls),
           'noncompleted_records_with_usage':sum(cost_r(r,True)>0 for r in fail)})
res['structure']={}
for arm in ['D-SELF','D-FRONT']:
    res['structure'][arm]={}
    for label,rows in [('all_completed_records',[r for r in raw if r['status']=='completed' and r['arm']==arm]),('latest_completed',[r for r in latest.values() if r['status']=='completed' and r['arm']==arm])]:
        us=[u for r in rows for u in [r.get('designer_usage'),r.get('designer_usage_repair')]+[s.get('usage') for s in r.get('steps',[])]]
        gates=[any(s.get('type') in ('if','while') for s in r.get('steps',[])) for r in rows]
        res['structure'][arm][label]={'n':len(rows),'total_tokens_field_only':sum(tokens(u) for u in us),'normalized_io_tokens':sum(tokens(u,True) for u in us),
            'designer_tokens_normalized':sum(tokens(u,True) for r in rows for u in [r.get('designer_usage'),r.get('designer_usage_repair')]),
            'executor_tokens_normalized':sum(tokens(s.get('usage'),True) for r in rows for s in r.get('steps',[])),
            'mean_designed':float(np.mean([r['n_steps'] for r in rows])), 'mean_executed_field':float(np.mean([r['executed_steps'] for r in rows])),
            'mean_logged_steps':float(np.mean([len(r.get('steps',[])) for r in rows])), 'with_gates':sum(gates),'gate_percent':100*sum(gates)/len(rows)}
res['cost_limitations']=['Frozen economics counts completed ledger rows, not unique latest keys, omits repair usage and failed attempts; checkpoint-resumed designs can have empty designer_usage.',
 'Recorded noncompleted costs are NOT safely summable to campaign cost: checkpointed step usage can recur across retries and provider attempts may lack usage. Missing usage is not zero cost.',
 'Frozen structure total_tokens ignores Anthropic input_tokens/output_tokens; executed_steps can count only resumed session while steps retains prior checkpoint steps.',
 'F-S-N split 15% input / 85% output is estimated, not measured. No billing invoices audited.']
# Trace source csv/JSON reproduction without overwriting originals.
res['artifact_comparisons']={}
for filename in ['study3_vs_fsn_full.csv','study3_contrast_a.csv','study3_contrast_a_composite.csv','study3_contrast_b.csv','study3_cost_structure.csv','study3_economics.csv','study3_participant_flow.csv','study3_by_family_domain.csv','study3conf_gates.csv','study3_vs_fsn_by_domain.csv']:
    rows=list(csv.DictReader((ROOT/'analysis/results'/filename).open()))
    res['artifact_comparisons'][filename]={'row_count':len(rows),'rows':rows}
(OUT/'study3_audit_diagnostics.json').write_text(dump(res)+'\n')
print('Novelty paired Student t:',[(r['family'],r['paired_t'],r['p_paired_two'],r['student_p_holm']) for r in res['authorship']['Novelty']])
print('Composite paired Student t:',[(r['family'],r['paired_t'],r['p_paired_two'],r['student_p_holm']) for r in res['authorship']['Composite']])
print('Flow:',fi['latest_counts'],cfi['latest_counts'])
print('Structure:',res['structure'])
print('Protocol16 diagnostics:',[(r['family'],r['d_pooled'],r['welch_df'],r['p_welch_two'],r['paired_t'],r['p_paired_two']) for r in res['protocol16_tests']['Novelty']])
print('Cost:',res['costs'])
