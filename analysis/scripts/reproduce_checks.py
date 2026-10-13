# Compilation and analysis: Friendly Society of Corvids.
"""Run the numerical checks offline from the fixed inputs in the analysis pack."""
import csv,json,math,pathlib
import numpy as np
from scipy.optimize import minimize
from scipy.special import expit

BASE=pathlib.Path(__file__).resolve().parent.parent
DATA=BASE/'data'
if not DATA.exists():DATA=pathlib.Path(__file__).resolve().parent/'deliverables'
rows=list(csv.DictReader((DATA/'artifact_counts.csv').open()))
output={}
for window in ['all','recent','seed','live']:
 selected=[r for r in rows if r['window']==window]
 X=[];y=[];n=[];num=den=0
 for i,r in enumerate(selected):
  a=int(r['trans_marked_blocked']);nt=int(r['trans_marked_total']);c=int(r['other_blocked']);no=int(r['other_total'])
  num+=a*(no-c)/(nt+no);den+=(nt-a)*c/(nt+no)
  for group,total,success in [(1,nt,a),(0,no,c)]:
   X.append([1,group]+[int(i==j) for j in range(1,4)]);y.append(success);n.append(total)
 X=np.asarray(X,float);y=np.asarray(y,float);n=np.asarray(n,float)
 def objective(b):return np.sum(n*np.logaddexp(0,X@b)-y*(X@b))
 def grad(b):return X.T@(n*expit(X@b)-y)
 f=minimize(objective,np.zeros(5),jac=grad,method='BFGS',options={'gtol':1e-8})
 assert np.max(np.abs(grad(f.x)))<1e-5
 p=expit(X@f.x);se=math.sqrt(np.linalg.inv(X.T@((n*p*(1-p))[:,None]*X))[1,1])
 output[window]={'band_only_or':math.exp(f.x[1]),'ci95':[math.exp(f.x[1]-1.96*se),math.exp(f.x[1]+1.96*se)],'mantel_haenszel_or':num/den}
expected=json.loads((DATA/'results.json').read_text())
for w,r in output.items():
 assert abs(r['band_only_or']-expected['aggregate_checks'][w]['bin_adjusted_logistic_or'])<1e-9
sources=list(csv.DictReader((DATA/'verified_sample_sources.csv').open()))
assert len(sources)==13
prior=[r for r in sources if r['predates_block']=='True']
assert len(prior)==10
assert sum(r['directly_replies_or_quotes_aaron']=='False' for r in prior)==8
print(json.dumps({'aggregate_models':output,'exact_sample_matches':len(sources),'preblock_posts':len(prior),'outside_direct_scope':8,'checks':'passed'},indent=2))
