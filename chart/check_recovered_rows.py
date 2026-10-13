# Compilation and analysis: Friendly Society of Corvids.
"""Verify decoded chart rows and fit a declared subset of the original model.

This cannot validate source-post coverage, identity labels, or campaign conduct.
"""
from pathlib import Path
import json,math
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

root=Path(__file__).resolve().parent
d=json.loads((root/'embedded_chart_data.json').read_text())
rows=json.loads((root/'anonymous_account_rows.json').read_text())
assert len(rows)==d['windows']['all']['accounts']==1678
assert sum(x['blocked'] for x in rows)==d['windows']['all']['blocked']==564
for band in range(4):
 for label,marker in [('trans',True),('other',False)]:
  subset=[x for x in rows if x['toxicity_band']==band and x['trans_explicit']==marker]
  expected=d['windows']['all']['bands'][band][label]
  assert len(subset)==expected['n']
  assert sum(x['blocked'] for x in subset)==expected['k']
X=np.array([[1,int(x['trans_explicit'])]+[int(x['toxicity_band']==k) for k in range(1,4)]+[int(x['quoted_aaron'])] for x in rows],float)
y=np.array([x['blocked'] for x in rows],float)
def objective(b):return np.sum(np.logaddexp(0,X@b)-y*(X@b))
def gradient(b):return X.T@(expit(X@b)-y)
fit=minimize(objective,np.zeros(X.shape[1]),jac=gradient,method='BFGS',options={'gtol':1e-8})
assert np.max(np.abs(gradient(fit.x)))<1e-5
p=expit(X@fit.x)
se=math.sqrt(np.linalg.inv(X.T@((p*(1-p))[:,None]*X))[1,1])
print(json.dumps({'rows':len(rows),'blocked':int(sum(y)),
 'model':'Blocked ~ trans_explicit + toxicity_band_fixed_effects + quoted_aaron',
 'odds_ratio':math.exp(fit.x[1]),
 'wald_ci95':[math.exp(fit.x[1]-1.96*se),math.exp(fit.x[1]+1.96*se)],
 'published_full_model':d['windows']['all']['odds'],
 'scope':'Partial model check; not a campaign-adjusted analysis or independent validation of labels'},indent=2))
