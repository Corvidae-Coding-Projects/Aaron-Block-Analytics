Compiled and analyzed by Friendly Society of Corvids.

Recovered partial data from the published Autoblock Audit
Retrieved 13 October 2026

Source: https://claude.ai/artifact/Fiy5MLT3eSoNnXZ5Rpfey7

The artifact's source contains a literal JSON object named D. Its four 'units'
strings encode the 1,678 accounts in the all-since-January visualization. The
published visualization maps each character through the base-32 alphabet:

    0123456789abcdefghijklmnopqrstuv

The resulting number contains five bits:
    1: blocked
    2: bio/name marked explicitly trans by the author's classification
    4: bio/name marked as having any trans signal by the author
    8: bio/name marked as listing pronouns by the author
   16: account quoted Aaron at least once

The position in one of the four strings gives the toxicity band:
    0: below 0.02
    1: 0.02 to 0.1
    2: 0.1 to 0.5
    3: above 0.5

Files
-----
embedded_chart_data.json: factual embedded chart object, including aggregate
tables, packed flags, and precomputed odds ratios / intervals / p-values.
anonymous_account_rows.json / .csv: decoded anonymous rows.
recovered_data_check.json: results of a limited numerical model check.
check_recovered_rows.py: reproduce that check with numpy and scipy installed.

Run:
    python check_recovered_rows.py

The synthetic anonymous_row identifiers are positions created during decoding.
They are not author-provided account IDs or stable public identifiers. DO NOT
join these rows to the recovered public block/post records by position.

The decoded counts exactly reproduce the published all-window band tables:
1,678 accounts, 564 blocked, 127 marked explicitly trans. A logistic model using
the trans marker, four toxicity bands, and quote status returns OR 2.4651,
95% Wald interval 1.6462-3.6914. The embedded published fuller model reports
OR 2.48, interval 1.65-3.73. This shows numerical coherence, not causal attribution.

Still missing
-------------
The mapping from anonymous rows to accounts; the exact source posts; historical
profile snapshots and identity patterns; continuous toxicity scores; per-account
post counts, swearing and threat features; the full regression specification;
and account-level membership in the other three analysis windows.

Neither the embedded object nor the inspected visualization logic includes an
account/post ID mapping, those per-account inputs, or a data-download link. The
visualization displays precomputed regression outputs; it does not fit the full
model in the browser. The source labels have not been independently validated.

Surviving public posts, current bios, and blocks can support an independent
reconstruction. They cannot recover the author's exact historical sample or
restore deleted material. The earlier source-linked contextual findings remain
separate until a valid account/post mapping is available.
