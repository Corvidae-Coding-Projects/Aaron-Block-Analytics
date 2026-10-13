Compiled and analyzed by Friendly Society of Corvids.

Autoblock Audit: contextual analysis materials
13 October 2026

The PDF is supplied separately. This package contains fixed aggregate inputs,
computed results, timestamped source metadata, a factual current block-record
snapshot, and collection / verification scripts. It does not contain the
artifact author's missing account-level labels, scores, or regression data.

Offline numerical reproduction
-----------------------------
Install numpy and scipy in your preferred Python environment, then run:

    python scripts/reproduce_checks.py

The program reproduces all four band-only logistic fits from data/artifact_counts.csv
and verifies the 13 exact source matches, 10 pre-block posts, and 8 off-scope
posts in the retained metadata. It does not independently authenticate those
source texts offline. Source-post URLs and SHA-256 text hashes allow checking
against current public records.

Files and definitions
---------------------
artifact_counts.csv: manual transcription of the published audit's four tables.
results.json: computed descriptive results, fitted numerical checks, coverage
limitations, and explicitly hypothetical omitted-behavior sensitivity inputs.
blocks_by_day.csv: independently recovered block records grouped by UTC date.
block_record_snapshot.json: 1,284 factual block records, including 1,271 with
record timestamps in the audit window. No biographies are included.
verified_sample_sources.csv: exact source matches to 13 of Aaron's 50 examples.
context_source_metadata.csv: 28 sexual-allegation reference candidates. These
include questions and rebuttals; they are not automatically harassment labels.
source_manifest.json: retrieval time, URL, status, and raw-response file hashes.

Temporal flags use parsed record timestamps. Blocks removed before collection,
deleted posts, and past profile descriptions are not recoverable from a current
snapshot. 'No block found' is not a guarantee that no historical block occurred.

Fresh public collection
-----------------------
The scripts collect read-only public API data. They do not log in, post, contact
anyone, or modify accounts. To repeat collection in a separate directory:

    python scripts/collect.py
    python scripts/search_context.py
    python scripts/collect_sample.py
    python scripts/verify_sample.py

Fresh searches may return different results or fail; the original run encountered
administrative rejection of several pagination requests. No population inference
is made from this incomplete search corpus. None of these scripts bypasses access
controls. Current API data cannot recreate a deleted historical record.

Interpretation
--------------
The band-only fits check numerical coherence of reported counts. They do not
reproduce the artifact's fuller model, validate its identity / toxicity labels,
or adjust for campaign participation. The required original account-level data
and a complete eligible comparison population were unavailable. The PDF states
that limitation and does not manufacture a corrected identity coefficient.

The report builder now creates the revised plain-language PDF. In the combined
repository, run python analysis/scripts/build_report.py. It also needs the
sibling mapping data, ReportLab and DejaVu Sans fonts.

Independent contribution, checked 13 October 2026
------------------------------------------------
Michael Paulauski (@mike10010100.com) is an independent analyst and is not a
member of Friendly Society of Corvids. His public thread prompted the added
checks in data/mike_analysis_verification.json and the fixed-revision classifier
run in data/toxicity_example_verification.json. Source metadata and correction
notes are in data/independent_source_metadata.json and the combined repository's
docs/independent-analysis.md. No campaign-adjusted identity effect is estimated.

Source: https://bsky.app/profile/mike10010100.com/post/3mxrorcrzjv23
