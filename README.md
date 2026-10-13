# Aaron Block Analytics

Compiled and analyzed by **Friendly Society of Corvids**. Published 13 October 2026.

## What we found

**The audit left documented relevant conduct out of its behavior comparison. It therefore does not establish anti-trans discrimination.**

The published audit scored hostile language in replies and quote posts directed at Aaron Rodericks. His initial block lists also considered posts elsewhere on Bluesky. We verified eight posts with harm-related language that appeared before their authors were blocked and fell outside the replies and quotes the audit scored.

That omission matters. Two people can have the same score for their direct interactions with Aaron while having different conduct elsewhere. Matching on that score does not establish equal behavior across the evidence used for initial selection.

The targeting context and the omitted conduct are documented. How much that conduct explains the overall blocking gap remains unmeasured.

## Start here

| Material | What it contains |
| --- | --- |
| [Plain-language report](reports/autoblock_context_review.pdf) | Review, evidence tables and credited independent verification |
| [Step-by-step explanation](docs/explanation.md) | The methodological problem in everyday language |
| [Mapped public posts](mapping/account_post_map.csv) | 40 selected posts with account/post IDs, links, dates, excerpts and coding |
| [Blocked-account map](mapping/block_account_map.csv) | 1,271 recovered accounts blocked during the study window |
| [Anonymous chart rows](chart/anonymous_account_rows.csv) | 1,678 rows decoded from the audit's visualization |
| [Original aggregate inputs](analysis/data/artifact_counts.csv) | The four published tables used for numerical checks |
| [Independent contribution](docs/independent-analysis.md) | Michael Paulauski's findings, society verification and correction notes |
| [Downloadable packages](archives/) | Attributed copies of all three recovered analysis archives |

## Evidence at a glance

| Finding | Count |
| --- | ---: |
| Recovered block records dated 28 September-8 October 2026, UTC | 1,271 |
| Blocks in the initial bulk imports | 1,087 (85.5%) |
| Anonymous account rows recovered from the visualization | 1,678 |
| Selected posts verified and mapped | 40 |
| Mapped posts created and indexed before known blocks | 20 posts from 18 authors |
| Exact source matches to the published 50-example list | 13 |
| Matched examples posted before their authors' blocks | 10 |
| Those pre-block examples outside the scored replies/quotes | 8 |

Within the audit's sample, the author-labelled account groups had different blocking rates, but the unvalidated identity labels and incomplete behavior comparison prevent those rates from establishing anti-trans discrimination: 74 of 127 accounts labelled explicitly trans were blocked (58.3%), versus 490 of 1,551 remaining accounts (31.6%). A model using toxicity bands and quote status gives an odds ratio of 2.465, close to the audit's reported fuller-model result of 2.48. These checks reproduce the author's numerical comparison; they do not independently validate its identity labels or causal interpretation.

The anonymous rows have no account-ID mapping. They must not be joined to the public account/post records by position or guessed feature matches. This repository contains no completed estimate of the blocking difference after accounting for the broader conduct.

## Reproduce the preserved checks

Run these commands from the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 analysis/scripts/reproduce_checks.py
python3 chart/check_recovered_rows.py
python3 scripts/check_mapping.py
python3 scripts/check_mike_analysis.py
```

The first check reproduces the four band-only models and the 13/10/8 sample counts. The second checks the decoded rows and the band-plus-quote model. The third verifies the preserved account/post mapping against the saved block snapshot and source metadata. The fourth reproduces the independent subgroup and date-cohort checks. These are offline checks of the retained records; they do not authenticate current public posts or estimate campaign prevalence.

## Credited independent analysis

**Michael Paulauski (@mike10010100.com) is an independent analyst and is not a member of Friendly Society of Corvids.** His [public thread](https://bsky.app/profile/mike10010100.com/post/3mxrorcrzjv23) identified additional checks that the society evaluated against the preserved data and primary posts.

We reproduced the pronoun-only subgroup counts, checked the corrected live-only figures and the date-cohort composition, and independently ran the named classifier on his example strings. We also re-retrieved two role-based harm posts illustrating the name-search blind spot. [Verification results](analysis/data/mike_analysis_verification.json), [classifier results](analysis/data/toxicity_example_verification.json) and [source metadata](analysis/data/independent_source_metadata.json) distinguish verified findings from unresolved claims.

The comparison category contains accounts with pronoun markers and no detected trans signal, as well as accounts with neither feature. The audit-defined profile flags are unvalidated and relevant conduct is omitted, so subgroup rates do not establish discrimination or its absence. This verifies that the comparator is heterogeneous; it does not identify why an account was blocked.

For optional classifier reproduction, install a CPU build of PyTorch and the packages in `requirements-model.txt`, then run:

```bash
python3 scripts/check_toxicity_examples.py
```

The script fixes the Hugging Face model revision and records software versions and the weights hash. It scores four supplied strings; it does not identify their original accounts or recover the audit's full preprocessing.

To regenerate the revised PDF, install the DejaVu Sans fonts and run:

```bash
python3 analysis/scripts/build_report.py
```

The historical collection and reconstruction scripts are retained in `analysis/scripts/` and `mapping/`. Fresh collection can return different records. `mapping/build_mapping.py` requires the raw post views and mapped evidence generated by `mapping/recover_evidence.py`; those raw inputs are not included in the preserved package. The [package notes](mapping/README.txt) explain the coverage limits.

## Scope and sources

This concerns personal account blocks, not platform suspensions. The selected posts document examples; they are not a representative sample of everyone blocked. Ordinary criticism and rebuttals are coded separately from accusations and harm-related language. The larger account-history collection was lost during an environment reset, so the findings use the preserved, rechecked records.

The original study is the [published Autoblock Audit](https://claude.ai/artifact/Fiy5MLT3eSoNnXZ5Rpfey7). Source links and hashes accompany the evidence. The society's attribution covers the compilation and original analysis; public posts and the original audit retain their source authorship. See [ATTRIBUTION.md](ATTRIBUTION.md).
