"""Audit-only diagnostics. Never execute source mains or modify source artifacts."""
import json, sys, itertools, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
import statsmodels.formula.api as smf
import statsmodels.api as sm
ROOT = Path('/Users/youssefhariri/Documents/app 25/research/orchestration-economics')
OUT = ROOT/'paper/P5_v14.3-audit-2026-09-16'
sys.path.insert(0, str(ROOT/'code'))
import analyze_main as am
import analyze_exploratory as ae
import refine_study2_analyze as ra
warnings.filterwarnings('ignore', category=UserWarning)
def load(p): return json.loads((ROOT/p).read_text())
def plain(v):
    if isinstance(v, dict): return {str(k):plain(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [plain(x) for x in v]
    if isinstance(v,np.ndarray): return v.tolist()
    if isinstance(v,np.generic): return v.item()
    return v
store=load('runs/fulltext/main_fulltext.json')
meta={r['runId']:r for r in store['runs'] if r.get('fulltext')}
recs,bad=am.load_judgments(ROOT/'runs/logs/main_judgments.jsonl')
df=am.build_run_table(recs,meta)
raw=[json.loads(x) for x in (ROOT/'runs/logs/main_judgments.jsonl').read_text().splitlines() if x.strip()]
raw_agg=ra.agg(raw)
ledger=[r for r in load('runs/logs/main_run_ledger.json')['results'] if r['status']=='completed']
led=pd.DataFrame([{k:r[k] for k in ['runId','cell','family','problemId','totalTokensUsed','totalLatencyMs']} for r in ledger])
dm=load('data/problems/domain_map.json')['map']
df=df.merge(led[['runId','totalTokensUsed','totalLatencyMs']],on='runId',validate='one_to_one')
df['domain']=df.problemId.map(dm)
legacy=df.copy()
legacy['composite']=legacy.runId.map(lambda i:raw_agg[i]['composite'])
for dim in am.DIMS: legacy['d_'+dim]=legacy.runId.map(lambda i:raw_agg[i][dim])
res={'data':{'main_runs':len(df),'problems':df.problemId.nunique(),'families':df.family.nunique(),'valid_judgments':len(recs),'bad_last_records':bad,'raw_records':len(raw),'n_judgments_distribution':df.n_judg.value_counts().to_dict(),'run_composites_changed_unfiltered_legacy':int((abs(df.composite-legacy.composite)>1e-12).sum()),'max_change_unfiltered_legacy':float(abs(df.composite-legacy.composite).max())}}
agg=pd.read_csv(ROOT/'evaluation/scores_aggregated.csv')
agg=agg[agg.study=='study1_main']
aggm=agg.groupby('run_id').composite.mean()
compare=df.set_index('runId').composite.to_frame('filtered').join(aggm.rename('export'))
res['data']['scores_aggregated_main_rows']=len(agg)
res['data']['aggregated_export_max_abs_composite_difference']=float(abs(compare.filtered-compare.export).max())
ix=am.interaction_stats(df); ix.pop('cells')
ix['bootstrap95CI']=am.boot_ci_interaction(df)
ix['BF10']=am.jzs_bf(ix['t'],ix['n']/4,ix['df'])
res['primary_interaction']=ix
res['main_effects']={}
for factor,pos,neg in [('tier','F','C'),('structure','T','S'),('persona','P','N')]:
    a=df[df[factor]==pos].composite.to_numpy(); b=df[df[factor]==neg].composite.to_numpy()
    t,dof,p,d,n=am.welch_two(a,b)
    sp=np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
    res['main_effects'][factor]={'mean_difference':a.mean()-b.mean(),'d_total_SD':d,'d_within_group_pooled_SD':(a.mean()-b.mean())/sp,'t':t,'df':dof,'p':p,'n':n,'bootstrap95CI':am.boot_ci_two(a,b),'BF10':am.jzs_bf(t,len(a)*len(b)/(len(a)+len(b)),dof)}
res['persona_dimensions']=ae.a3_5_dimensions(df)
aov=smf.ols('composite ~ C(tier)*C(structure)*C(persona)',df).fit()
at=sm.stats.anova_lm(aov,typ=2)
res['anova']={'df_resid':aov.df_resid,'terms':at.to_dict('index'),'shapiro_p':stats.shapiro(aov.resid).pvalue,'levene_p':stats.levene(*[g.composite.to_numpy() for _,g in df.groupby('cell')]).pvalue}
res['family_loo']={}
for f in sorted(df.family.unique()):
    z=am.interaction_stats(df[df.family!=f]); z.pop('cells'); res['family_loo'][f]=z
res['problem_loo']={}
for f in sorted(df.problemId.unique()):
    z=am.interaction_stats(df[df.problemId!=f]); z.pop('cells'); res['problem_loo'][f]=z
res['minimum_detectable_d']=am.sensitivity_power(190,.05)
reg=df.assign(loglen=np.log(df.fulltextLen),tier=df.tier.map({'F':1,'C':0}),structure=df.structure.map({'T':1,'S':0}),persona=df.persona.map({'P':1,'N':0}))
res['length_primary']={}
for lab,form in [('unadjusted','composite ~ tier*structure*persona'),('adjusted','composite ~ tier*structure*persona + loglen')]:
    m=smf.ols(form,reg).fit(cov_type='HC1')
    marginal=m.t_test('tier:structure + 0.5*tier:structure:persona = 0')
    res['length_primary'][lab]={'conditional_N_coef':m.params['tier:structure'],'conditional_N_p':m.pvalues['tier:structure'],'marginal_interaction_coef':float(np.asarray(marginal.effect).ravel()[0]),'marginal_interaction_p':float(marginal.pvalue),'marginal_interaction_CI':marginal.conf_int().tolist()}
res['meta_EB']=ae.a3_3_4_families(df)
meta_r=res['meta_EB']['meta']
res['meta_EB']['normal_prediction_interval_approx']=[meta_r['pooled_d']-1.96*np.sqrt(meta_r['tau2']+meta_r['se']**2),meta_r['pooled_d']+1.96*np.sqrt(meta_r['tau2']+meta_r['se']**2)]
res['paired_diagnostics']={}
for unit in [['family','problemId'],['problemId']]:
    p=df.pivot_table(index=unit,columns=['tier','structure'],values='composite',aggfunc='mean')
    delta=p[('F','T')]-p[('F','S')]-p[('C','T')]+p[('C','S')]
    t,pv=stats.ttest_1samp(delta,0)
    res['paired_diagnostics']['interaction_'+'_'.join(unit)]={'n':len(delta),'df':len(delta)-1,'mean':delta.mean(),'d_z':delta.mean()/delta.std(ddof=1),'t':t,'p':pv,'note':'Replicates and personas averaged first. Family-problem units share both families and problems; 95-unit test is descriptive, not a crossed-RE solution.'}
res['ctp_fsn_family']={}
for f,g in df.groupby('family'):
    p=g.pivot_table(index='problemId',columns='cell',values='composite',aggfunc='mean')
    delta=p['C-T-P']-p['F-S-N']; z=ra.paired_stats(delta.to_numpy(),5000)
    z['df']=len(delta)-1; z['p_two']=stats.ttest_1samp(delta,0).pvalue
    a=g[g.cell=='C-T-P'].composite.to_numpy(); b=g[g.cell=='F-S-N'].composite.to_numpy()
    sp=np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
    z['independent_d_pooled']=(a.mean()-b.mean())/sp
    z['independent_d_total_SD']=am.welch_two(a,b)[3]
    res['ctp_fsn_family'][f]=z
ps=multipletests([v['p_two'] for v in res['ctp_fsn_family'].values()],method='holm')[1]
for v,p in zip(res['ctp_fsn_family'].values(),ps): v['p_two_holm']=p
# Alternative pairing used in Study 2 sample, including any repeated baseline.
pairs=load('runs/refine/sample_pilot.json')['pairs']+load('runs/refine/sample_extension.json')['pairs']
q=df.set_index('runId').composite
res['ctp_fsn_refinement_samples']={}
for f in ['kimi','claude','qwen']:
    pr=[p for p in pairs if p['family']==f]
    dd=np.array([q[p['ctp_runId']]-q[p['fsn_runId']] for p in pr])
    res['ctp_fsn_refinement_samples'][f]=ra.paired_stats(dd)|{'unique_FSN':len({p['fsn_runId'] for p in pr}),'unique_CTP':len({p['ctp_runId'] for p in pr})}
# Cost figures recomputed from raw tokens and current frozen-vector subset.
prices=load('config/price_vector.json')['prices']; registry=load('config/model_registry.json')['generators']
for phi in [.25,.5,.75]:
    def cfun(r):
        model=registry[r.family]['cheap_sibling' if r.tier=='C' else 'frontier']['model']; p=prices[model]
        return r.totalTokensUsed*((1-phi)*p['input']+phi*p['output'])/1e6
    df['cost_'+str(phi)]=df.apply(cfun,axis=1)
res['cell_summary']=df.groupby('cell').agg(n=('runId','size'),mean_quality=('composite','mean'),sd_quality=('composite','std'),mean_tokens=('totalTokensUsed','mean'),mean_cost=('cost_0.5','mean'),latency_ms=('totalLatencyMs','mean')).to_dict('index')
res['pareto']={}
for phi in [.25,.5,.75]:
    tb=df.groupby('cell').agg(cost=('cost_'+str(phi),'mean'),quality=('composite','mean'))
    res['pareto'][str(phi)]=[c for c,v in tb.iterrows() if not any(o!=c and w.cost<=v.cost and w.quality>=v.quality and (w.cost<v.cost or w.quality>v.quality) for o,w in tb.iterrows())]
res['tegr']={}
for cell in sorted(df.cell.unique()):
    ratios={k:[] for k in ['novelty','composite']}
    for f,g in df.groupby('family'):
        b=g[g.cell=='F-S-N']; a=g[g.cell==cell]
        for name,col in [('novelty','d_Novelty'),('composite','composite')]: ratios[name].append((a[col].mean()/b[col].mean())/(a['cost_0.5'].mean()/b['cost_0.5'].mean()))
    res['tegr'][cell]={k:np.mean(v) for k,v in ratios.items()}
res['twins']={}
for c in ['C-S','C-T','F-S','F-T']:
    p=res['cell_summary'][c+'-P']; n=res['cell_summary'][c+'-N']
    res['twins'][c]={'quality_P_minus_N':p['mean_quality']-n['mean_quality'],'cost_P_minus_N':p['mean_cost']-n['mean_cost'],'cost_percent_change':100*(p['mean_cost']/n['mean_cost']-1),'token_P_minus_N':p['mean_tokens']-n['mean_tokens']}
# Legacy heterogeneity uses ALL raw judgments, including retries/partial/error records.
res['heterogeneity']={}
for name,table in [('filtered',df),('legacy_unfiltered',legacy)]:
    sub=table[table.cell.isin(['C-S-N','C-T-N','F-S-N'])]
    dom=sub.pivot_table(index='domain',columns='cell',values='composite',aggfunc='mean')
    fam=sub.pivot_table(index='family',columns='cell',values='composite',aggfunc='mean')
    gap=fam['F-S-N']-fam['C-S-N']; team=fam['C-T-N']-fam['C-S-N']; relative=fam['C-T-N']-fam['F-S-N']
    r_true=stats.pearsonr(gap,team); r_shared=stats.pearsonr(gap,relative)
    perms=list(itertools.permutations(relative.to_numpy()))
    exact_p=sum(abs(stats.spearmanr(gap,p).statistic)>=abs(stats.spearmanr(gap,relative).statistic)-1e-12 for p in perms)/len(perms)
    res['heterogeneity'][name]={'domain_team_minus_cheap_solo':(dom['C-T-N']-dom['C-S-N']).to_dict(),'domain_team_minus_frontier_solo':(dom['C-T-N']-dom['F-S-N']).to_dict(),'family_gap_FSN_CSN':gap.to_dict(),'family_team_CTN_CSN':team.to_dict(),'family_relative_CTN_FSN':relative.to_dict(),'r_gap_true_team':r_true.statistic,'p_gap_true_team':r_true.pvalue,'r_gap_relative_team':r_shared.statistic,'p_gap_relative_team':r_shared.pvalue,'rho_gap_relative_team':stats.spearmanr(gap,relative).statistic,'exact_two_sided_spearman_p':exact_p}
# Reproduce executed mixed models without writes. vc_formula under family creates family-specific problem effects,
# and with re_formula omitted there is NO separate family random intercept.
res['legacy_mixed_models']={}
sub=legacy[legacy.cell.isin(['C-S-N','C-T-N','F-S-N'])].copy();sub['logtok']=np.log(sub.totalTokensUsed)
m=smf.mixedlm("composite ~ logtok + C(cell, Treatment('C-S-N'))",sub,groups=sub.family,vc_formula={'problem':'0 + C(problemId)'}).fit(reml=True)
res['legacy_mixed_models']['three_cell']={'params':m.fe_params.to_dict(),'p':m.pvalues.to_dict(),'k_re':m.model.k_re,'k_vc':m.model.k_vc}
sub=legacy[legacy.tier=='C'].copy();sub['team']=sub.structure=='T';sub['persona']=sub.persona=='P';sub['logtok']=np.log(sub.totalTokensUsed)
res['legacy_mixed_models']['persona']={}
for col in ['composite','d_Novelty','d_Usefulness','d_Cultural Sensitivity']:
    sub['outcome']=sub[col]
    m=smf.mixedlm('outcome ~ logtok + team*persona',sub,groups=sub.family,vc_formula={'problem':'0 + C(problemId)'}).fit(reml=True)
    res['legacy_mixed_models']['persona'][col]={'params':m.fe_params.to_dict(),'p':m.pvalues.to_dict(),'k_re':m.model.k_re,'k_vc':m.model.k_vc}
# All diagnostics serialized only in the authorized audit directory.
(OUT/'study1_diagnostic_values.json').write_text(json.dumps(plain(res),indent=2,allow_nan=False)+'\n')
print(json.dumps(plain({k:res[k] for k in ['data','primary_interaction','length_primary','ctp_fsn_family','ctp_fsn_refinement_samples','heterogeneity','tegr','twins']}),indent=2))
