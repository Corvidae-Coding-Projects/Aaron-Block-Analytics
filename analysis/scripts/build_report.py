# Compilation and analysis: Friendly Society of Corvids.
from pathlib import Path
import csv
import html
import json

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ANALYSIS = Path(__file__).resolve().parent.parent
ROOT = ANALYSIS.parent
DATA = ANALYSIS / 'data'
MAPPING = ROOT / 'mapping'
if not MAPPING.exists():
    MAPPING = ROOT / 'account_post_mapping'
OUT = ROOT / 'reports' / 'autoblock_context_review.pdf'
OUT.parent.mkdir(parents=True, exist_ok=True)
RESULTS = json.loads((DATA / 'results.json').read_text())
SUMMARY = json.loads((MAPPING / 'mapping_summary.json').read_text())
RECOVERED = json.loads((MAPPING / 'recovered_data_check.json').read_text())
EXTERNAL = json.loads((DATA / 'mike_analysis_verification.json').read_text())
MODEL_CHECK_PATH = DATA / 'toxicity_example_verification.json'
MODEL_CHECK = json.loads(MODEL_CHECK_PATH.read_text()) if MODEL_CHECK_PATH.exists() else None
ARTIFACT = 'https://claude.ai/artifact/Fiy5MLT3eSoNnXZ5Rpfey7'
SOURCE_SHEET = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSqDngHpDnBvSvSxvxaJO4679WlwqfNBgPsX3qJMqWMHJlUmHlZ0siklD73gZI-5fTX1S6bpKB2ifdj/pubhtml'

pdfmetrics.registerFont(TTFont('ReportSans', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('ReportSans-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('ReportSans', normal='ReportSans', bold='ReportSans-Bold', italic='ReportSans', boldItalic='ReportSans-Bold')
INK = colors.HexColor('#292629')
OXBLOOD = colors.HexColor('#54252e')
PARCHMENT = colors.HexColor('#f4f1eb')
styles = {
    'title': ParagraphStyle('title', fontName='ReportSans-Bold', fontSize=22, leading=27, textColor=OXBLOOD, spaceAfter=13),
    'heading': ParagraphStyle('heading', fontName='ReportSans-Bold', fontSize=16, leading=20, textColor=OXBLOOD, spaceAfter=13),
    'body': ParagraphStyle('body', fontName='ReportSans', fontSize=10.2, leading=14.1, textColor=INK, spaceAfter=10),
    'small': ParagraphStyle('small', fontName='ReportSans', fontSize=8.7, leading=12, textColor=colors.HexColor('#4b4648'), spaceAfter=8),
    'cell': ParagraphStyle('cell', fontName='ReportSans', fontSize=8.6, leading=11.7, textColor=INK),
    'cellhead': ParagraphStyle('cellhead', fontName='ReportSans-Bold', fontSize=8.6, leading=11.7, textColor=colors.white),
    'callout': ParagraphStyle('callout', fontName='ReportSans-Bold', fontSize=12, leading=16.4, textColor=OXBLOOD, spaceAfter=12),
}
story = []
plain = []

# Sources are cited where they enter the argument, including external findings.
REFS = [
    ('Published audit and embedded chart data', ARTIFACT),
    ('Autoblocker announcement, 30 September 2026', 'https://bsky.app/profile/aaron.bsky.team/post/3mwqe37envs2x'),
    ('Initial-list clarification, 30 September 2026', 'https://bsky.app/profile/aaron.bsky.team/post/3mwqeidhoo22w'),
    ('Sitewide-query explanation, 1 October 2026', 'https://bsky.app/profile/aaron.bsky.team/post/3mwsv6uvlrc27'),
    ('Identity and opt-in statement, 1 October 2026', 'https://bsky.app/profile/aaron.bsky.team/post/3mwsv6uvvjs27'),
    ('Public 50-interaction example sheet', SOURCE_SHEET),
    ('Aaron\'s accidental-like explanation, 6 October 2025', 'https://bsky.app/profile/aaron.bsky.team/post/3m2kgo3c3bk2u'),
    ('Contemporaneous likes/bot dispute reference, 22 December 2024', 'https://bsky.app/profile/did:plc:wl5vrrccbahchjq7mrbo34yd/post/3ldwllzl3ok2x'),
    ('Public repetition of the porn allegation, 8 May 2026', 'https://bsky.app/profile/grinzhy.bsky.social/post/3mle4wkudg22t'),
    ('Aaron\'s moderation and camps discussion, 16 September 2026', 'https://bsky.app/profile/aaron.bsky.team/post/3mvobdemx6v25'),
    ('Michael Paulauski\'s independent analysis thread', 'https://bsky.app/profile/mike10010100.com/post/3mxrorcrzjv23'),
    ('Michael Paulauski\'s live-only correction', 'https://bsky.app/profile/mike10010100.com/post/3mxru63thls26'),
    ('Audit author\'s clarification of the bot headline', 'https://bsky.app/profile/aidap.bsky.social/post/3mxrulsvkqk2u'),
    ('Audit author\'s discussion of harshness and camp references', 'https://bsky.app/profile/aidap.bsky.social/post/3mxrulsvkql2u'),
    ('Toxicity classifier model card', 'https://huggingface.co/unitary/unbiased-toxic-roberta'),
    ('AT Protocol repository specification', 'https://atproto.com/specs/repository'),
    ('Verified account/post mapping and coding', 'https://github.com/Corvidae-Coding-Projects/Aaron-Block-Analytics/blob/main/mapping/account_post_map.csv'),
    ('Reproduction results and source metadata', 'https://github.com/Corvidae-Coding-Projects/Aaron-Block-Analytics/tree/main/analysis/data'),
]

def p(text, style='body'):
    story.append(Paragraph(text, styles[style]))
    plain.append(text)

def heading(text):
    p(text, 'heading')

def page():
    story.append(PageBreak())

def link(label, url):
    return f'<link href="{html.escape(url, quote=True)}" color="#71333c">{html.escape(label)}</link>'

def cite(*numbers):
    return ' ' + ' '.join(link(f'[{n}]', REFS[n - 1][1]) for n in numbers)

def aaron(key):
    return 'https://bsky.app/profile/aaron.bsky.team/post/' + key

def table(rows, widths):
    converted = [[Paragraph(str(cell), styles['cellhead' if i == 0 else 'cell']) for cell in row] for i, row in enumerate(rows)]
    item = Table(converted, colWidths=widths, repeatRows=1, hAlign='LEFT')
    item.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), OXBLOOD),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [PARCHMENT, colors.white]),
        ('LINEBELOW', (0, 0), (-1, 0), .5, OXBLOOD),
        ('LINEBELOW', (0, 1), (-1, -1), .3, colors.HexColor('#ddd8d0')),
    ]))
    story.extend([item, Spacer(1, 12)])
    plain.extend(' | '.join(str(v) for v in row) for row in rows)

# Page 1: the combined finding, with context and attribution up front.
p('Personal blocks, harassment,<br/>and the audit', 'title')
p('By <b>Friendly Society of Corvids</b><br/>13 October 2026 | Integrated evidence review<br/>Block-record window: 28 September to 8 October 2026, inclusive, UTC.', 'small')
p('The audit does not establish anti-trans discrimination. Its behavior comparison leaves out documented targeted abuse and combines different routes to a personal block.', 'callout')
p('Aaron Rodericks and his Trust &amp; Safety team were the subjects of repeated sexual accusations, harm wishes and a call for mass suicide harassment. Relevant posts were public before the block imports. Aaron described selecting an initial list from abuse across Bluesky; the audit compared accounts using only replies and quotes directed at him. Those are different records of conduct.' + cite(3, 4, 6, 17))
p('<b>The omissions compound one another.</b> A post can target someone by job title, appear outside their replies, and use language whose harm depends on context. The audit can miss that post or give it a very low score, then treat its author as comparable to someone whose relevant conduct was different.')
table([
    ['Finding', 'Verified evidence', 'Consequence'],
    ['Harassment outside the scored activity', '8 pre-block examples outside direct replies/quotes', 'Matching scores do not establish matching conduct.'],
    ['Two blocking processes combined', '1,087 of 1,271 blocks imported in bulk (85.5%)', 'The combined result cannot be presented as a live-bot result.'],
    ['Context lost by the classifier', 'All 4 checked strings score below 0.02', 'The lowest score band does not certify harmless conduct.'],
    ['Comparison population changes', 'Distinct profile subgroups and 466 additional all-year accounts', 'The result depends on who is being compared.'],
], [166, 170, 180])
p('<b>A separate criticism does hold:</b> the broad description of blocking as entirely opt-in does not cover imported lists that required no new direct interaction. ' + cite(3, 5))
p('Michael Paulauski (' + link('@mike10010100.com', REFS[10][1]) + ') is an independent analyst and <b>is not a member of Friendly Society of Corvids</b>. His public analysis prompted checks incorporated throughout this report. The society verified the cited counts, source records and classifier tests; corrections and remaining gaps are identified with the relevant findings.', 'small')

# Page 2: the campaign and the actual selection process.
page()
heading('The campaign preceded the block imports')
p('The public record documents sustained targeting across several episodes. Some posts criticized moderation policy; others repeated sexual accusations, used sexualized ridicule, or described harm to Aaron and Trust &amp; Safety staff. We keep those categories separate. Mentioning the dispute, asking a question, or quoting an accusation to reject it is not itself coded as harassment.' + cite(17))
table([
    ['Date', 'Record and context'],
    ['22 Dec 2024', 'A contemporaneous post referred to a third day of demands over a likes-monitoring bot. This documents an early dispute, rather than its complete origin.' + cite(8)],
    ['6 Oct 2025', 'Aaron said a bot captured an accidental like/unlike during a spam investigation and that harassment continued. This is his explanation; original like logs were not recovered.' + cite(7)],
    ['8 May 2026', 'A public post repeated the porn allegation, showing that the accusation persisted into 2026.' + cite(9)],
    ['16-25 Sep 2026', 'Aaron\'s 16 September moderation thread discussed a camps reference. Six mapped authors posted sexual-allegation references before bulk blocks; these include criticism and inquiry, not six uniformly coded harassment cases.' + cite(10, 17)],
    ['17-18 Sep 2026', 'Verified posts included stabbing-related language aimed at Trust &amp; Safety and an explicit call for users to tell its head to kill himself. Both preceded the authors\' blocks.' + cite(17)],
    ['30 Sep-1 Oct 2026', 'Three bulk imports preceded the public autoblocker announcement. Aaron then described both incoming-interaction automation and a seed list selected through an AI query of sitewide abuse.' + cite(2, 3, 4)],
], [98, 418])
p('<b>The harassment is independently documented.</b> The source dates place relevant abuse before the imports. The explicit call for collective harassment establishes coordination rhetoric; the records do not identify a central organizer or measure how many people acted on that call.')
p('<b>The initial lists and the later bot require separate analysis.</b> The snapshot contains 1,271 blocks in the window: 1,087 bulk imports and 184 other blocks. Those totals describe block records, while the audit\'s live-only comparison contains 413 sampled accounts. They are different populations.' + cite(1, 18))
p('An imported list can block an account without a new reply or quote. The broad opt-in claim is therefore inaccurate for the combined process. Aaron publicly disclosed a seed set; that disclosure and the opt-in problem should both remain visible.' + cite(3, 5))

# Page 3: observed omissions and timing, with source links.
page()
heading('The audit left relevant posts out')
p('The audit scored hostile language in replies and quotes directed at Aaron. His account of initial selection describes a sitewide search for abuse. We matched 13 of his 50 published examples to exact public source text after normalizing case, whitespace and typographic quotes.' + cite(1, 4, 6))
verified = list(csv.DictReader((DATA / 'verified_sample_sources.csv').open()))
descriptions = {
    2: 'Home-targeting / burning imagery',
    12: 'Head injury language',
    15: 'Death-related conditional statement',
    16: 'Illegal / divine retribution framing',
    19: 'Stabbing T&S; heads',
    21: 'Broken bones / tire iron',
    23: 'Government beating',
    24: 'Police beating T&S; heads',
    26: 'Death in a fictional chemical vat',
    28: 'Coordinated suicide encouragement',
    36: 'Imprisonment and death wish',
    37: 'Ambiguous wish to be next',
    44: 'Child-sexual-offending allegation',
}
rows = [['Sheet row', 'Language in the post', 'Post date', 'Before block?', 'Direct reply / quote?']]
for r in verified:
    n = int(r['sample_row'])
    before = 'Yes' if r['predates_block'] == 'True' else ('No' if r['block_record_time_utc'] else 'No current block')
    rows.append([link(str(n), r['source_url']), descriptions[n], r['created_at_utc'][:10], before, 'Yes' if r['directly_replies_or_quotes_aaron'] == 'True' else 'No'])
table(rows, [53, 172, 83, 101, 107])
p('<b>Ten matched posts preceded blocks; eight were outside the scored replies and quotes.</b> This establishes a concrete omission in the behavior comparison. It does not establish that every author is identifiable in the anonymous regression sample.')
p('Rows 19 and 28 also demonstrate Mike\'s name-search concern: they refer to the head of Trust &amp; Safety using harm-related language, contain neither Aaron nor Roderick, and precede the authors\' third-bulk blocks. A search for his name cannot establish absence of targeting.' + cite(11))
p('Row 44 followed its author\'s block and cannot explain that earlier decision. Rows 23 and 37 have no corresponding block in the current snapshot. The wider mapping contains 40 selected posts; 20 posts from 18 authors were both created and indexed before their known blocks.', 'small')

# Page 4: contextual meaning and the independently run classifier.
page()
heading('A low score does not mean harmless conduct')
p('There are two failures to account for: relevant posts were outside the scored set, and the score itself does not capture all relevant meaning. A threat, an insinuation, or a recurring sexual accusation can be written without profanity. Equal generic toxicity scores do not establish equal harassment.' + cite(1, 15))
p('Mike supplied four classifier test strings. The society independently ran them through the named model at a fixed revision. <b>All four score below the audit\'s 0.02 cutoff for its lowest band.</b> These are test inputs, not factual endorsements or proof of original sample membership.' + cite(11, 18))
rows = [['Classifier test string', 'Independent toxicity score']]
for example in MODEL_CHECK['examples']:
    rows.append([html.escape(example['text']), f"{example['independent_score']:.6f}"])
table(rows, [346, 170])
p('Three of Mike\'s rounded scores reproduce. The fourth is 0.000628 in this run, compared with his reported 0.00191; both are below 0.02. These scores cannot substitute for reviewing the conduct in context.')
p('<b>The camps references need their actual context.</b> Aaron\'s 16 September thread discussed someone else\'s statement contrasting trans rights with camps. Critics disputed his interpretation and later returned the phrase at him. The audit author describes that contested callback in her clarification. A camps reference alone is insufficient to classify a post as a literal threat.' + cite(10, 14))
p('That dispute does not erase the independently verified stabbing language and mass suicide-harassment call. Their wording supplies evidence of harm and collective targeting beyond a camp callback. Each post should be assessed using its target, surrounding discussion and timing, rather than its profanity count.')
p('<b>A name-only search has a separate blind spot.</b> The chart reports 178 no-contact cases across all three imports (15 + 72 + 91), with 91 in the third import. The two role-based examples establish that a name search can miss abuse. The unpublished membership of the 178-account cohort prevents us from counting how many of those cases it misclassified. We do not repeat Mike\'s description of all 178 as third-import cases.' + cite(1, 11))
p('Model: unitary/unbiased-toxic-roberta; revision ' + MODEL_CHECK['revision'] + '. CPU evaluation; sigmoid of the toxicity output; maximum 512 tokens. Saved results include software versions and the weights hash. The model card also explains that profanity can receive high scores irrespective of intent.' + cite(15, 18), 'small')

# Page 5: comparator and date-cohort findings integrated into the argument.
page()
heading('Who gets compared changes the result')
p('The audit\'s remaining-account group combines different profile categories. Mike identified that the decoded chart separates accounts with pronouns but no detected trans signal from accounts with neither feature. Their recorded blocking rates differ substantially. These are <b>the audit\'s profile flags, not independently validated gender identities</b>.' + cite(1, 11))
rows = [['Audit-defined category', 'Blocked / accounts', 'Recorded rate']]
labels = {'explicit_trans_marker': 'Explicit trans marker', 'other_trans_signal': 'Other trans signal', 'pronouns_only': 'Pronouns, no detected trans marker', 'neither_marker_nor_pronouns': 'Neither detected trans marker nor pronouns'}
for key, label in labels.items():
    g = EXTERNAL['groups'][key]
    rows.append([label, f"{g['blocked']} / {g['accounts']}", f"{100*g['rate']:.1f}%"])
table(rows, [280, 123, 113])
p('These categories exhaust the 1,678 decoded rows. The subgroup counts and rounded rates reproduce exactly. Pronoun-only accounts have about twice the recorded blocking odds of accounts with neither feature: crude odds ratio 2.164; our band-adjusted check gives 2.126 (95% interval 1.634-2.765). Mike reports a nearby adjusted result of 2.11.' + cite(18))
p('<b>This is a problem for a simple trans-versus-everyone-else interpretation.</b> The remaining group is not a uniform comparison population. Similar observed rates in two subgroups do not prove equivalent treatment. The profile patterns do not establish why accounts were selected, and neither pronouns nor an absent marker identify an account\'s participation in the campaign.')
p('<b>The date window changes the population too.</b> The all-year window contains 466 accounts absent from the recent window. Of its 395 additional unblocked accounts, 390 (98.7%) lack the explicit trans marker. Adding this older comparison population changes the baseline against which the recent blocking dispute is assessed.' + cite(1, 11, 18))
p('The band-only estimate falls from 2.64 for the all-year sample to 2.04 for the recent sample. This demonstrates sensitivity to the chosen comparison window. It does not measure campaign participation or establish that the additional accounts were all ordinary, unrelated interactions.')
p('Subtracting individual toxicity-band cells cannot uniquely identify earlier-only accounts: a shared account can move bands when its highest-scoring post changes between windows. We therefore retain the verified 466-account total and 98.7% composition figure, without claiming an identified 314-account historical cohort or a demonstrated Simpson\'s paradox.', 'small')
p('Our adjusted pronoun comparison gives p = 1.93 x 10^-8; Mike reports 1.5 x 10^-8. The exact adjusted figures are close, not identical, and his full model specification was not supplied. These differences do not change the verified subgroup counts.', 'small')

# Page 6: numerical consistency, process separation and the author clarification.
page()
heading('What the statistical results actually establish')
p('The audit\'s numerical association is reproducible. In its sample, 74 of 127 explicitly trans-labelled accounts were blocked (58.3%), versus 490 of 1,551 remaining accounts (31.6%). <b>Those are sample rates under unvalidated labels and an incomplete conduct measure.</b> They establish an association within the collected records, without identifying its cause.' + cite(1, 18))
p('An odds ratio compares blocking odds within a model; it is not a multiplier of the probability of being blocked. Adding toxicity bands and quote status to our decoded-row model gives 2.465 (95% interval 1.646-3.691), close to the audit\'s fuller-model 2.48 (1.65-3.73). This verifies numerical consistency while leaving the measurement problems intact.')
rows = [['Accounts included', 'Audit\'s reported odds ratio (95% interval)', 'Our band-only check (95% interval)']]
windows = {
    'all': ('All since January', '2.5 (1.6-3.7)'),
    'recent': ('Since 15 September', '2.0 (1.3-3.0)'),
    'seed': ('Before bulk imports', '2.8 (1.7-4.5)'),
    'live': ('Incoming blocks, initial-list accounts excluded', '1.7 (0.8-3.8)'),
}
for key, (label, estimate) in windows.items():
    r = RESULTS['aggregate_checks'][key]
    lo, hi = r['bin_adjusted_logistic_ci95']
    rows.append([label, estimate, f"{r['bin_adjusted_logistic_or']:.2f} ({lo:.2f}-{hi:.2f})"])
table(rows, [170, 173, 173])
p('<b>The live-only result cannot sustain a 2.5-2.8-fold bot-discrimination headline.</b> The corrected live-only sample has 413 accounts, including 30 with the explicit marker and 13 of those blocked. Its published model output is 1.70 (95% interval 0.76-3.78), p = 0.196. The interval covers equal odds and substantially higher odds: the live-only data are too imprecise to settle a group difference.' + cite(12))
p('In her public clarification, the audit author acknowledges that her opener made the finding sound like it came from the bot and that the bot-only result is too small to call. She also identifies the generic harshness measure as the weaker part. These clarifications belong alongside the findings they qualify.' + cite(13, 14))
p('Mike\'s later correction supersedes N=674 and his original lowest-band figures. The corrected next-lowest band is 1/5 versus 13/42; the lowest band is 3/11 versus 41/224. A non-significant result does not establish absence of bias. Our band-only fits and decoded-row fit are partial reproductions; the original fuller regression was not refitted.', 'small')

# Page 7: the actual combined judgment and its finite evidentiary boundary.
page()
heading('The combined finding')
p('<b>The record documents harassment that the audit\'s comparison did not adequately measure.</b> That judgment rests on dated public posts, independently matched examples, the sitewide-selection statement and actual classifier tests. The omissions are demonstrated by the retained records.')
p('The failures occur at different stages. A name search misses targeting by job title. Reply-and-quote scoring misses posts elsewhere. A generic score can treat context-dependent harm language as very mild. Combining imported lists with incoming blocks then obscures which selection process produced the association. Changing profile subgroups and date windows further changes the comparison.')
p('<b>Taken together, these findings undermine the claim that the audit compared people whose relevant conduct was the same.</b> The observed blocking gap is compatible with unmeasured differences in targeting and campaign participation. The analysis cannot separate that explanation from identity-based selection. Presenting the residual score-adjusted association as established anti-trans discrimination goes beyond the evidence.')
p('One mapped account, whose bio observed on 13 October described its owner as cishet, repeated the porn allegation at 13:29:36.938 UTC on 30 September; its block record follows at 13:29:47, about ten seconds later. This is a concrete cross-identity example of accusation-related conduct preceding a block. A single sequence does not explain every block or establish how the system processed that post.' + cite(17))
p('<b>The unresolved quantity is the campaign\'s contribution to the overall gap.</b> The anonymous chart has no account-ID mapping. We cannot join the verified posts to its rows and calculate a valid campaign-adjusted identity effect. The validity of every block and the possibility of bias remain separate questions.')
p('The conclusion concerns documented conduct by particular accounts. It does not describe trans people as a group. Policy criticism, neutral inquiry and rebuttal remain separate from abuse. The allegation posts establish that accusations were made; this report makes no finding that those accusations are true.')
heading('What is preserved, and what a stronger test needs')
p('The retained evidence includes 1,284 current block subjects (1,271 in the study window), 1,678 anonymous chart rows and 40 selected mapped posts. The selected posts are not a representative sample. Searches were incomplete, removed posts and blocks are missing, and one reader coded the text. All 41 earlier provenance-table entries retained their text hashes on re-retrieval; one post appears in both tables.', 'small')
p('A stronger test needs the original account/post mapping, comparable frozen pre-decision histories for both groups, historical profile labels and the actual selection criteria. It should analyze imports and incoming blocks separately, validate conduct in context, and measure collection loss. Neither a partial reconstruction nor the present selected examples supplies that missing estimate.', 'small')

# Page 8: a unified source list and reproducibility record.
page()
heading('Sources and verification record')
p('Numbered links in the report point to the sources below. Individual rows in the matched-example table link directly to their public posts. Source authors retain authorship of their material. Compilation, verification and this report are attributed to Friendly Society of Corvids.', 'small')
for i, (label, url) in enumerate(REFS, 1):
    p(f'{i}. ' + link(label, url), 'small')
heading('Reproducibility and attribution')
p('Michael Paulauski (@mike10010100.com) is credited as an independent analyst and non-member. His original thread, correction and the audit author\'s responses are primary-source inputs. The society\'s checks reproduce his subgroup counts and date-window totals, use his corrected live-only figures, independently run his four model strings, and verify the role-based source examples.', 'small')
p('The repository includes the decoded chart data, original aggregate tables, mapped source IDs and timestamps, hashes, coding notes and numerical results. Offline checks: analysis/scripts/reproduce_checks.py; chart/check_recovered_rows.py; scripts/check_mapping.py; scripts/check_mike_analysis.py. Classifier reproduction: scripts/check_toxicity_examples.py, with its fixed model revision. The PDF is generated by analysis/scripts/build_report.py.', 'small')
p('Mike\'s claimed 2/25 identity-label errors, exact membership of the 178-account no-contact cohort, differential post-recovery loss and the share of blocks explained by May or September events were not independently established. They are excluded from measured conclusions. Detailed corrections remain in docs/independent-analysis.md. This review concerns personal account blocks, not platform suspensions.', 'small')

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#ddd8d0'))
    canvas.line(48, 38, 564, 38)
    canvas.setFont('ReportSans', 7.5)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(48, 25, 'Friendly Society of Corvids | Autoblock methodology review | 13 October 2026')
    canvas.drawRightString(564, 25, str(doc.page))

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=48, rightMargin=48, topMargin=44, bottomMargin=50,
                        title='Personal blocks, harassment, and the audit', author='Friendly Society of Corvids',
                        subject='Integrated review of campaign context, selection, measurement and verified independent findings')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
