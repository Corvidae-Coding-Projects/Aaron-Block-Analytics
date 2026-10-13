"""Verify numeric checks proposed by independent analyst Michael Paulauski.

Verification: Friendly Society of Corvids. Michael Paulauski is not a member.
Uses the preserved audit chart object and its independently decoded rows.
"""
from pathlib import Path
import argparse
import json
import math

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit
from scipy.stats import fisher_exact, norm

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('--output', type=Path)
args = parser.parse_args()
d = json.loads((ROOT / 'chart/embedded_chart_data.json').read_text())
decoded = json.loads((ROOT / 'chart/anonymous_account_rows.json').read_text())

def category(r):
    return ('explicit_trans_marker' if r['trans_explicit'] else
            'other_trans_signal' if r['any_trans_signal'] else
            'pronouns_only' if r['pronouns_listed'] else 'neither_marker_nor_pronouns')

groups = {g: [0, 0] for g in ['explicit_trans_marker', 'other_trans_signal', 'pronouns_only', 'neither_marker_nor_pronouns']}
for r in decoded:
    group = groups[category(r)]
    group[0] += int(r['blocked'])
    group[1] += 1
assert groups == {'explicit_trans_marker': [74, 127], 'other_trans_signal': [76, 170],
                  'pronouns_only': [184, 445], 'neither_marker_nor_pronouns': [230, 936]}
assert sum(n for _, n in groups.values()) == 1678
assert sum(k for k, _ in groups.values()) == 564
a, na = groups['pronouns_only']
c, nc = groups['neither_marker_nor_pronouns']
crude = fisher_exact([[a, na - a], [c, nc - c]])
comparison = fisher_exact([[76, 170 - 76], [a, na - a]])

subset = [r for r in decoded if not r['trans_explicit'] and not r['any_trans_signal']]
x = np.array([[1, int(r['pronouns_listed'])] + [int(r['toxicity_band'] == b) for b in [1, 2, 3]] for r in subset], float)
y = np.array([int(r['blocked']) for r in subset], float)
fit = minimize(lambda beta: np.sum(np.logaddexp(0, x @ beta) - y * (x @ beta)), np.zeros(5),
               jac=lambda beta: x.T @ (expit(x @ beta) - y), method='BFGS', options={'gtol': 1e-8})
assert np.max(np.abs(x.T @ (expit(x @ fit.x) - y))) < 1e-5
prob = expit(x @ fit.x)
se = math.sqrt(np.linalg.inv(x.T @ ((prob * (1 - prob))[:, None] * x))[1, 1])

all_window = d['windows']['all']
recent = d['windows']['recent']
live = d['windows']['live']
early_accounts = all_window['accounts'] - recent['accounts']
early_unblocked = (all_window['accounts'] - all_window['blocked']) - (recent['accounts'] - recent['blocked'])
early_other_unblocked = ((all_window['overall']['other']['n'] - all_window['overall']['other']['k']) -
                         (recent['overall']['other']['n'] - recent['overall']['other']['k']))
assert (early_accounts, early_unblocked, early_other_unblocked) == (466, 395, 390)
assert live['accounts'] == 413 and live['trans'] == 30
assert live['bands'][1]['trans']['k'] == 1 and live['bands'][1]['trans']['n'] == 5
assert live['bands'][1]['other']['k'] == 13 and live['bands'][1]['other']['n'] == 42

result = {
    'verification_attribution': 'Friendly Society of Corvids',
    'independent_contributor': {'name': 'Michael Paulauski', 'handle': 'mike10010100.com',
                               'society_member': False, 'thread_url': 'https://bsky.app/profile/mike10010100.com/post/3mxrorcrzjv23'},
    'classification_scope': 'Audit-defined profile flags, not independently verified personal identities or campaign participation.',
    'groups': {g: {'blocked': k, 'accounts': n, 'rate': k / n} for g, (k, n) in groups.items()},
    'pronouns_only_vs_neither': {
        'crude_odds_ratio': float(crude.statistic), 'fisher_two_sided_p': float(crude.pvalue),
        'band_adjusted_odds_ratio': math.exp(fit.x[1]),
        'band_adjusted_wald_ci95': [math.exp(fit.x[1] - 1.96 * se), math.exp(fit.x[1] + 1.96 * se)],
        'band_adjusted_wald_p': float(2 * norm.sf(abs(fit.x[1] / se))),
        'mike_reported_odds_ratio': 2.11, 'mike_reported_p': 1.5e-8,
        'verification': 'Counts and rates reproduced exactly. Our specified models give nearby but non-identical adjusted statistics; his exact model specification was not supplied.'},
    'other_trans_signal_vs_pronouns_only': {
        'fisher_two_sided_p': float(comparison.pvalue),
        'interpretation': 'Similar observed percentages; a non-significant test does not establish equivalence.'},
    'window_composition': {
        'all_minus_recent_accounts': early_accounts, 'all_minus_recent_unblocked': early_unblocked,
        'unblocked_without_explicit_trans_marker': early_other_unblocked,
        'fraction_without_explicit_marker': early_other_unblocked / early_unblocked,
        'interpretation': 'Account-level subtraction uses the audit-defined nested date cohorts. Per-band subtraction cannot uniquely identify earlier-only accounts because a shared account may change its harshest-post band between windows.'},
    'live_only': {
        'accounts': live['accounts'], 'explicit_marker_accounts': live['trans'],
        'blocked_explicit_marker_accounts': live['overall']['trans']['k'],
        'published_model_odds_ratio': live['odds'][0], 'published_model_ci95': live['odds'][1:], 'published_model_p': live['p'],
        'mild_explicit': {'blocked': 1, 'accounts': 5}, 'mild_remaining': {'blocked': 13, 'accounts': 42},
        'very_mild_explicit': {'blocked': 3, 'accounts': 11}, 'very_mild_remaining': {'blocked': 41, 'accounts': 224},
        'verification': 'Counts and precomputed model output checked against the preserved source object; the original fuller regression was not refitted.',
        'correction_source': 'https://bsky.app/profile/mike10010100.com/post/3mxru63thls26',
        'superseded': 'Earlier thread figures N=674 and very-mild rates 5.9% vs 6.2% are not used.'},
    'conclusion_scope': 'Establishes omitted-context, comparator-composition and score-validation problems. Does not estimate a campaign-adjusted identity effect or prove that every block was justified.',
}
text = json.dumps(result, indent=2)
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text + '\n')
print(text)
