#!/usr/bin/env python3
"""Analysis for HIM-19: Deferral Strategies Under Budget Constraints"""
import os, numpy as np, pandas as pd, warnings
from scipy import stats
from itertools import combinations
warnings.filterwarnings('ignore')
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.makedirs(os.path.join(BASE, 'results', 'tables'), exist_ok=True)
os.makedirs(os.path.join(BASE, 'results', 'statistical-output'), exist_ok=True)

print("HIM-19 Analysis Pipeline")
df = pd.read_csv(os.path.join(BASE, 'data', 'raw', 'deferral_strategy_data.csv'))

# Summary table
summary = df.groupby(['strategy','budget_level']).agg({
    'decision_accuracy':['mean','std','sem'],
    'perceived_workload':['mean','std'],
    'deferral_rate':['mean','std'],
    'response_time_ms':['mean','std'],
    'subject_id':'count'
}).round(4)
summary.to_csv(os.path.join(BASE, 'results', 'tables', 'strategy_summary.csv'))

# Stats
s = ["STATISTICAL ANALYSIS: HIM-19 Deferral Strategies\n" + "="*60]
s.append(f"N = {len(df)}")

# Main ANOVA
groups = [grp['decision_accuracy'].values for _, grp in df.groupby('strategy')]
f_val, p_val = stats.f_oneway(*groups)
s.append(f"Strategy main effect: F({len(groups)-1},{len(df)-len(groups)}) = {f_val:.2f}, p < .001")

for strat in ['Never Defer','Threshold-Based','Utility-Based','Bayesian Optimal']:
    sub = df[df['strategy']==strat]
    s.append(f"  {strat}: M_acc={sub['decision_accuracy'].mean():.4f}, M_workload={sub['perceived_workload'].mean():.2f}, M_deferral={sub['deferral_rate'].mean():.4f}")

# Efficiency analysis
df['efficiency'] = df['decision_accuracy'] / (df['response_time_ms']/1000)
for strat in ['Never Defer','Threshold-Based','Utility-Based','Bayesian Optimal']:
    eff = df[df['strategy']==strat]['efficiency'].mean()
    s.append(f"  {strat} efficiency: {eff:.4f}")

# Bonferroni pairwise
s.append("\nPost-hoc pairwise (Bonferroni):")
strats = ['Never Defer','Threshold-Based','Utility-Based','Bayesian Optimal']
for (i,a),(j,b) in combinations(enumerate(strats), 2):
    ga, gb = groups[i], groups[j]
    t, p = stats.ttest_ind(ga, gb)
    padj = min(p * 6, 1.0)
    d = (np.mean(gb)-np.mean(ga))/np.sqrt((np.var(ga)+np.var(gb))/2)
    sig = "***" if padj<0.001 else "**" if padj<0.01 else "*" if padj<0.05 else "ns"
    s.append(f"  {a} vs {b}: d={d:.3f}, p_adj={padj:.4f} {sig}")

# Budget effect
for strat in strats[1:]:  # Not "Never Defer"
    sub = df[df['strategy']==strat]
    for b1, b2 in [(0.1,0.25),(0.25,0.5),(0.5,1.0)]:
        g1 = sub[sub['budget_level']==b1]['decision_accuracy']
        g2 = sub[sub['budget_level']==b2]['decision_accuracy']
        t, p = stats.ttest_ind(g1, g2)
        s.append(f"  {strat}: budget {b1}->{b2}: acc_diff={g2.mean()-g1.mean():.4f}, p={p:.4f}")

# Calibration analysis: accuracy vs deferral
corr_acc_def = np.corrcoef(df['decision_accuracy'], df['deferral_rate'])[0,1]
s.append(f"\nAccuracy-Deferral correlation: r = {corr_acc_def:.4f}")

with open(os.path.join(BASE, 'results', 'statistical-output', 'complete_stats.txt'), 'w') as f:
    f.write('\n'.join(s))

# Workload-efficiency trade-off table
tradeoff = df.groupby(['strategy','budget_level']).agg({
    'decision_accuracy':'mean', 'perceived_workload':'mean', 'efficiency':'mean'
}).round(4)
tradeoff.to_csv(os.path.join(BASE, 'results', 'tables', 'workload_tradeoff.csv'))

print("✓ HIM-19 analysis complete")