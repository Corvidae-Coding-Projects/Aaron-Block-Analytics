Compiled and analyzed by Friendly Society of Corvids.

Account/post mapping and methodology check — 13 October 2026

Finding: the audit omitted documented relevant conduct from its behavior
comparison. It therefore does not establish anti-trans discrimination. This
package provides a verified mapping of selected evidence; the contribution of
the broader conduct to the overall sample difference remains unmeasured.

Files
block_account_map.csv: all 1,271 recovered block subjects in 28 September–8 October,
with record IDs, CIDs, dates, bulk-import classification and selected evidence counts.
A zero selected-evidence count DOES NOT mean no abuse occurred: histories are incomplete.
account_post_map.csv: 40 selected public posts with stable actor/post IDs, links,
record/index/block timestamps, short excerpts, source hashes and text-reviewed context.
source_metadata.json and retrieval_log.json: observed source metadata for 44 posts,
including Aaron’s explanation and description of the sitewide seed query.
anonymous_account_rows.json and embedded_chart_data.json: the chart’s anonymous data.
check_recovered_rows.py: reproducible numerical check; requires NumPy and SciPy.
recovered_data_check.json: preserved result of the subset-model numerical check.

Verification
Every evidence post was retrieved again. All 41 provenance-table entries retained
the same text hash as the earlier capture (one post occurs in both tables).
Mapped block dates exactly match the saved block-record snapshot. Twenty unique
selected posts have both record-created and AppView index timestamps before their
known block. Of the published hand-selected examples, 10 posts from 9 blocked
accounts predate blocking; 8 are outside direct reply/quote scoring.
These are selected examples, not a representative sample or a prevalence estimate.

Coding
Flags describe language in a post, not established facts about Aaron or a finding
about the writer’s motive. Plain porn-like references, policy criticism, neutral
questions and rebuttals are separated from sexual allegations/ridicule and harm
rhetoric. The quoted allegation in the rebuttal post is not coded as endorsement.
Ambiguous harm/sexual rhetoric is marked separately. One reader did the coding;
there was no independent second coder. No gender identity is inferred for these
mapped authors, and no claim is made that all criticism belongs to a campaign.

What remains missing
1. The original author’s account-ID and post-ID/CID mapping for the 1,678 anonymous rows.
   1,668 rows share their encoded feature combination with another row. Even unique
   combinations cannot be safely identified without the original sampling/coding rules.
2. Frozen pre-decision post histories and historical profile snapshots for both
   blocked and comparison accounts, including deletion/collection coverage.
3. Exact toxicity scores, post counts, swear/threat features, preprocessing,
   inclusion rules, model code, and the seed-selection query/lookback.
4. A complete comparison cohort with equivalent retrieval and context coding.

The subset numerical model reproduces an odds ratio of 2.465 (95% model-based
interval 1.646–3.691), close to the published full-model 2.48. It uses toxicity-band
indicators and quote status. It does not validate the full original regression,
source-post coverage, identity labels or causal interpretation.

A sound further test should separate bulk imports from incoming blocks; use a
common pre-import cutoff; count only conduct available before the decision;
compare the same accounts before/after adding contextual conduct; and examine
missingness, sparse cells and alternative identity/context definitions. A residual
association would not itself establish intent; attenuation would not prove no bias.

Status of this attempt
A much larger collection was attempted but lost when the working environment reset.
It was not preserved well enough to report a verifiable adjusted result. This package
contains only recovered, independently rechecked material. No campaign-adjusted
effect estimate is claimed. The earlier limited context report remains valid.

This is evidence about personal block records, not platform suspensions. Aaron’s
account of an accidental like during an investigation is a public statement, not
independent proof of the accident. Campaign origin, coordination, and the truth
of sexual allegations are not established by this mapping.
