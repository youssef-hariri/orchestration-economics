"""Read-only methods audit diagnostics; no existing runner imports or API calls.
Only output is stdout. Run with PYTHONDONTWRITEBYTECODE=1.
"""
from pathlib import Path
import json
from collections import Counter, defaultdict
import random
import numpy as np
ROOT = Path('/Users/youssefhariri/Documents/app 25/research/orchestration-economics')
def load(p):
    return json.loads((ROOT / p).read_text())
def lines(p):
    with (ROOT / p).open() as f:
        return [json.loads(s) for s in f if s.strip()]
out = {}
main = load('runs/logs/main_run_ledger.json')['results']
completed = [r for r in main if r.get('status') == 'completed']
team = [r for r in completed if r['cell'].split('-')[1] == 'T']
retry = [r for r in team if len(r.get('steps', [])) > 3]
out['main'] = {
    'rows':len(main), 'completed':len(completed), 'problem_count':len({r['problemId'] for r in completed}),
    'families':dict(Counter(r['family'] for r in completed)),
    'cells':dict(Counter(r['cell'] for r in completed)),
    'team_completed':len(team), 'team_more_than_3_step_records':len(retry),
    'step_count_distribution':dict(Counter(len(r['steps']) for r in team)),
    'team_ledger_equals_sum_steps':sum(r['totalTokensUsed'] == sum(s.get('tokensUsed') or 0 for s in r['steps']) for r in team),
    'failed_step_tokens':dict(Counter(s.get('tokensUsed') for r in team for s in r['steps'] if s.get('status') != 'completed')),
    'team_by_tier':dict(Counter(r['tier'] for r in team)),
    'in_discount_window_field_present':sum('in_discount_window' in r for r in completed),
    'started_min':min(r['startedAtUtc'] for r in completed), 'started_max':max(r['startedAtUtc'] for r in completed),
    'qwen_inside_14_24':sum(14 <= int(r['startedAtUtc'][11:13]) < 24 for r in completed if r['family']=='qwen'),
    'truncatedAtSource_count':sum(bool(r.get('truncatedAtSource')) for r in completed),
    'fulltextSource':dict(Counter(r.get('fulltextSource') for r in completed)),
    'failed_steps_sample':[{'runId':r['runId'],'cell':r['cell'],'steps':r['steps']} for r in retry[:2]]
}
for name, file in [('original','business_problems_15.json'),('domain_extension','business_problems_domain_15.json'),('fresh','fresh_business_cases_10.json'),('merged_main','business_problems_30.json')]:
    x=load('data/problems/'+file)
    if 'problems' in x:x=x['problems']
    out[name]={'count':len(x),'keys':list(x) if isinstance(x,dict) else None}
orig=load('data/problems/business_problems_15.json');ext=load('data/problems/business_problems_domain_15.json');merged=load('data/problems/business_problems_30.json')
for name,blob in [('orig',orig),('ext',ext)]:
    if 'problems' in blob:blob=blob['problems']
    out[name+'_verbatim_merge'] = all(merged[k]==v for k,v in blob.items())
out['domain_counts']=dict(Counter(load('data/problems/domain_map.json')['map'].values()))
# Replicate analyze_main's last-record-wins followed by error/incomplete filtering.
raw=lines('runs/logs/main_judgments.jsonl');last={}
for r in raw:last[(r['runId'],r['judge_family'],r['variant'])]=r
valid=[r for r in last.values() if not r.get('error') and not r.get('incomplete')]
byrun=Counter(r['runId'] for r in valid)
byjudge=defaultdict(lambda:defaultdict(list))
for r in valid:byjudge[r['judge_family']][r['runId']].append(np.mean([v for v in r['scores'].values() if isinstance(v,(int,float))]))
correlations={}
for a,b in [('deepseek','zhipu'),('deepseek','meta'),('meta','zhipu')]:
    ids=sorted(set(byjudge[a]) & set(byjudge[b]))
    correlations[a+'~'+b]={'n_common_runs':len(ids),'pearson_r':float(np.corrcoef([np.mean(byjudge[a][i]) for i in ids],[np.mean(byjudge[b][i]) for i in ids])[0,1])}
out['main_judgments']={'raw_rows':len(raw),'unique_keys':len(last),'valid_keys':len(valid),'dropped_latest_invalid':len(last)-len(valid),'per_solution_valid_count':dict(Counter(byrun.values())),'incomplete_solution_ids':{str(k):v for k,v in byrun.items() if v!=9},'judges':dict(Counter(r['judge_model'] for r in valid)),'resolved':dict(Counter(r.get('judge_model_resolved') for r in valid)),'variants':dict(Counter(r['variant'] for r in valid)),'max_tokens':dict(Counter(r.get('max_tokens') for r in valid)),'correlations':correlations}
# Coverage only, not Study-3 numerical reanalysis.
for name,file in [('wave','runs/logs/wave_judgments.jsonl'),('study3','runs/study3/study3_judgments_v2.jsonl'),('study3conf','runs/study3conf/study3conf_judgments.jsonl')]:
    rr=lines(file);ll={}
    for r in rr:
        if not r.get('error') and not r.get('incomplete'):ll[(str(r['runId']),r['judge_family'],r['variant'])]=r
    out[name+'_judge_coverage']={'valid_unique_keys':len(ll),'per_solution_count':dict(Counter(Counter(k[0] for k in ll).values()))}
wave=load('runs/logs/wave_run_ledger.json')['results'];wc=[r for r in wave if r.get('status')=='completed' and r.get('finalResponse')]
out['wave_design']={'problems':len({r['problemId'] for r in wc}),'families':sorted({r['family'] for r in wc}),'cells':sorted({r['cell'] for r in wc}),'kimi_frontier_pipelines':dict(Counter((str(r['projectId'])+' '+r['name']) for r in wc if r['family']=='kimi' and r['cell']=='F-S-N')),'overlap_with_main':sorted({r['problemId'] for r in wc}&{r['problemId'] for r in main})}
reg=load('config/model_registry.json');prices=load('config/price_vector.json')['prices']
out['price_ratios']={f:{'input':prices[g['frontier']['model']]['input']/prices[g['cheap_sibling']['model']]['input'],'output':prices[g['frontier']['model']]['output']/prices[g['cheap_sibling']['model']]['output'],'blend_50':sum(prices[g['frontier']['model']].values())/sum(prices[g['cheap_sibling']['model']].values())} for f,g in reg['generators'].items()}
# Actual fixed-pipeline configurations, not merely the experiment config.
registry=load('pipelines/fixed/fixed_pipelines_registry.json')
out['fixed_registry_entry_keys']=list(registry['created'][0])
for label,file in [('fixed','pipelines/fixed/fixed_pipelines_registry.json'),('wave_fixed','pipelines/fixed/wave_pipelines_registry.json')]:
    entries=load(file)['created'];stats=Counter()
    for e in entries:
        d=e.get('definition',{});steps=d.get('steps',[])
        for s in steps:stats[(str(s.get('model')),str(s.get('temperature')),str(s.get('maxTokens')))]+=1
    out[label+'_model_temp_cap']=[{'model':k[0],'temperature':k[1],'maxTokens':k[2],'n_steps':v} for k,v in stats.items()]
# Reproduce triple sample against frozen pair files; compare exact answer identities.
pairs=load('runs/refine/sample_pilot.json')['pairs']+load('runs/refine/sample_extension.json')['pairs']
rng=random.Random(20260801);picked=[]
for fam in ['kimi','claude','qwen']:picked+=rng.sample(sorted(p['ctp_runId'] for p in pairs if p['family']==fam),10)
texts={r['runId']:r.get('fulltext','') for r in load('runs/fulltext/main_fulltext.json')['runs']}
triples=load('runs/qual2/triples.json')['triples'];selected=sorted(picked)
out['qual_sample']={'triples':len(triples),'family_counts':dict(Counter(t['family'] for t in triples)),'seed_reproduces_original_texts':all(t['texts']['orig']==texts[i] for t,i in zip(triples,selected)),'paired_frontier_texts_match':all(t['texts']['fsn']==texts[next(p['fsn_runId'] for p in pairs if p['ctp_runId']==i)] for t,i in zip(triples,selected)),'unique_problem_family_pairs':len({(t['family'],t['problemId']) for t in triples})}
book=load('results/qual2_codebook.json')['items'];mat=defaultdict(dict)
for r in lines('runs/logs/qual2_closed.jsonl'):
    if r.get('vector') is not None:mat[r['key']][r['coder_family']]=r['vector']
a=[];b=[]
for c in book:
    for v in mat.values():
        if len(v)==2:a.append(v['deepseek'][c['id']]);b.append(v['zhipu'][c['id']])
po=np.mean(np.array(a)==np.array(b));pa=np.mean(a);pb=np.mean(b);pe=pa*pb+(1-pa)*(1-pb)
out['qual_kappa']={'paired_texts':len(mat),'codes':len(book),'code_rq_counts':dict(Counter(c['rq'] for c in book)),'binary_pairs':len(a),'observed_agreement':float(po),'pooled_kappa':float((po-pe)/(1-pe))}
# Only local registration state keys; no credentials, no network, no inferred timestamps.
out['local_registration_states']={}
for p in (ROOT/'preregistration/osf_submission').glob('.osf_state*.json'):
    x=json.loads(p.read_text());out['local_registration_states'][p.name]={k:v for k,v in x.items() if k in ['registration_id','public_url','node_id','draft_id']}
print(json.dumps(out,indent=2,default=str))
