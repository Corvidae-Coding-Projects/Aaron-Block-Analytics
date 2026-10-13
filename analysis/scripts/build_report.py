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

def p(text, style='body'):
    story.append(Paragraph(text, styles[style]))
    plain.append(text)

def heading(text):
    p(text, 'heading')

def page():
    story.append(PageBreak())

def link(label, url):
    return f'<link href="{html.escape(url, quote=True)}" color="#71333c">{html.escape(label)}</link>'

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

# Page 1: plain-language findings.
p('Autoblock Audit<br/>What the evidence shows', 'title')
p('Prepared for <b>Friendly Society of Corvids</b><br/>13 October 2026 - Revised with independently verified external analysis<br/>Blocks examined: 28 September to 8 October 2026, inclusive, UTC.', 'small')
p('The audit left documented relevant conduct out of its behavior comparison. It therefore does not establish anti-trans discrimination.', 'callout')
p('The audit compared accounts using a score for hostile language in replies and quotes directed at Aaron Rodericks. But the initial block lists also considered posts elsewhere on Bluesky. That left relevant conduct outside the comparison. We verified eight posts containing harm-related language that appeared before their authors were blocked and fell outside the text the audit scored.')
p('<b>This is a demonstrated flaw in the behavior comparison.</b> Matching accounts on a score that omits relevant posts does not show that those accounts behaved alike. The higher blocking rate cannot be attributed to trans identity from this analysis.')
table([
    ['Recovered evidence', 'Result', 'What it establishes'],
    ['Accounts blocked in the study window', '1,271', 'Matches the audit\'s total'],
    ['Blocks imported in three batches', '1,087 (85.5%)', 'Most blocks came from initial lists'],
    ['Anonymous account rows decoded from the chart', '1,678', 'The displayed counts can be reproduced'],
    ['Selected public posts verified and mapped', '40', 'Links posts to identifiable public accounts'],
    ['Mapped posts available before known blocks', '20 posts, 18 authors', 'Relevant conduct preceded those blocks'],
    ['Verified pre-block examples outside the scored replies/quotes', '8', 'The behavior score omitted relevant conduct'],
], [225, 96, 195])
p('Additional checks inspired by independent analyst Michael Paulauski examine the mixed comparison group and the generic toxicity score. The verified additions and his non-member attribution appear on pages 7-8.', 'small')
p('<b>The remaining question is how much the omitted conduct explains the blocking gap.</b> The preserved data do not provide a reliable numerical answer. The evidence is firm about the omission; its contribution to the overall gap is still unmeasured.')

# Page 2: chronology, separating records from explanations.
page()
heading('The accusation and blocking timeline')
p('Public posts document repeated sexual accusations and targeted abuse over the likes incident. The records below establish that this dispute existed before the September 2026 block imports.')
table([
    ['Date', 'Public record', 'What the record tells us'],
    ['22 Dec 2024', 'A contemporaneous post described a third day of demands over a bot made by Juni and tagged queen-of-the.pelf.ie.', 'The bot/likes dispute was already active. The bot creator\'s original post was not recovered.'],
    ['6 Oct 2025', link('Aaron\'s public explanation', aaron('3m2kgo3c3bk2u')) + ' says he accidentally liked a post while investigating a spam network, removed the like, and a bot captured it.', 'This is Aaron\'s account of the incident. The original like/unlike log and internal investigation records were unavailable.'],
    ['8 May 2026', link('A public post repeated the porn allegation', 'https://bsky.app/profile/grinzhy.bsky.social/post/3mle4wkudg22t') + '.', 'The allegation continued into 2026.'],
    ['16-25 Sep 2026', 'Six authors posted name-specific sexual-allegation references before their accounts entered the bulk block lists.', 'The accusation context preceded these six blocks.'],
    ['30 Sep 2026', link('The autoblocker announcement', aaron('3mwqe37envs2x')) + ' and ' + link('initial-list clarification', aaron('3mwqeidhoo22w')) + ' describe incoming interactions and an earlier set of accounts.', 'The initial block imports happened before the public announcement.'],
    ['1 Oct 2026', link('Aaron\'s explanation', aaron('3mwsv6uvlrc27')) + ' describes an AI query of sitewide posts and links ' + link('50 example interactions', SOURCE_SHEET) + '.', 'The initial selection considered more posts than the audit\'s reply/quote score covered.'],
], [78, 243, 195])
p('<b>The broader targeting context is documented.</b> Its relevance to the methodology comes from the recovered posts and their dates: accounts could be selected for conduct that the audit never included in their behavior score.')

# Page 3: exact matches and fuller verified mapping.
page()
heading('Verified posts and their timing')
p('We found exact source matches for 13 of Aaron\'s 50 published examples. The match required the full post text to agree after normalizing case, whitespace and typographic quotes. Each numbered entry below links to its public source.')
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
rows = [['Row', 'Language in the post', 'Post date', 'Before block?', 'Direct reply / quote?']]
for r in verified:
    n = int(r['sample_row'])
    before = 'Yes' if r['predates_block'] == 'True' else ('No' if r['block_record_time_utc'] else 'No current block')
    rows.append([link(str(n), r['source_url']), descriptions[n], r['created_at_utc'][:10], before, 'Yes' if r['directly_replies_or_quotes_aaron'] == 'True' else 'No'])
table(rows, [53, 172, 83, 101, 107])
p('<b>Ten matched examples preceded blocks. Eight of those were outside direct replies or quotes to Aaron.</b> Example 44 followed its author\'s block and cannot explain that earlier decision. Examples 23 and 37 had no corresponding block in the current snapshot.')
p('The later mapping contains 40 selected posts. Twenty posts from 18 authors were both created and indexed by Bluesky before their known blocks. All 41 entries in the two earlier evidence tables retained their original text hashes when retrieved again; one post appears in both tables.', 'small')

# Page 4: explain the methodological flaw without ritual qualifications.
page()
heading('Why the audit does not settle discrimination')
p('<b>1. It measured a narrower set of behavior than the blocking process considered.</b> The initial lists used sitewide posts. The audit scored replies and quotes directed at Aaron. That score leaves out harmful language posted elsewhere. The eight verified pre-block examples document harmful language outside the scored set.')
p('<b>2. Most blocks came from initial lists.</b> Three bulk imports account for 1,087 of the 1,271 blocks: 85.5%. Initial selection and later incoming-interaction blocking are different decisions. Combining them cannot isolate how the incoming-interaction bot behaved.')
p('<b>3. A non-trans example shows the targeting behavior crossed identity categories.</b> One account whose current bio described its owner as cishet repeated a porn allegation at 13:29:36.938 UTC on 30 September. Its block is timestamped 13:29:47 UTC, about ten seconds later. The profile was observed on 13 October.')
p('<b>4. The post coding separates accusations from ordinary discussion.</b> The mapped records distinguish sexual allegations, ridicule and harm-related language from neutral questions, rebuttals and policy criticism. A reference to the incident is not automatically counted as harassment. A rebuttal that quotes an accusation is not counted as endorsing it.')
p('<b>5. Reproducing the sample comparison does not establish discrimination.</b> Our numerical checks reproduce the audit author\'s group comparison. The identity labels were not independently validated, and the score omitted documented relevant conduct. The resulting difference cannot be attributed to identity from this analysis.')
p('The methodological judgment is clear: the audit omitted relevant conduct from its behavior comparison. Its sample comparison does not establish anti-trans discrimination.', 'callout')

# Page 5: retain the reproducible numbers and explain them.
page()
heading('The sample rates and numerical checks')
p('Within the audit\'s sample, the author-labelled groups had different blocking rates, but the unvalidated identity labels and incomplete behavior comparison prevent those rates from establishing anti-trans discrimination: <b>74 of 127 accounts labelled explicitly trans were blocked (58.3%)</b>, compared with <b>490 of 1,551 remaining accounts (31.6%)</b>.')
p('The first numerical check fitted a model to the four published toxicity bands. The table compares its results with the audit\'s reported fuller model. An odds ratio above 1 means higher blocking odds for the trans-labelled group within that model; it does not identify why the odds differ.', 'small')
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
p('<b>The decoded chart data give a closer check.</b> The visualization contains 1,678 anonymous account rows encoding blocked status, identity markers, quote status and toxicity band. Those rows reproduce the published combined counts exactly: 564 blocked accounts, including 74 of the 127 labelled explicitly trans.')
lo, hi = RECOVERED['wald_ci95']
p(f"Adding quote status to the band-based model gives an odds ratio of <b>{RECOVERED['trans_marker_odds_ratio']:.3f}</b>, with a 95% model-based interval of <b>{lo:.3f}-{hi:.3f}</b>. The audit reports 2.48 (1.65-3.73) for its fuller model. This close agreement establishes numerical consistency.")
p('<b>The separate incoming-block estimate is too imprecise to settle that part of the question.</b> Its reported interval, 0.8-3.8, includes equal odds and substantially higher odds. The combined result is dominated by the initial lists.')
p('The chart does not identify the accounts behind its rows. We therefore cannot attach the verified public posts to those anonymous rows and fit a valid model that adds the omitted conduct.', 'small')

# Page 6: put the real limits in one place and retain source links.
page()
heading('Evidence limits and source records')
p('<b>Scope.</b> This report examines Aaron\'s personal account blocks. It does not analyze platform suspensions. The current block snapshot contains 1,284 subjects, of which 1,271 have record timestamps in the study window. Deleted posts and removed blocks are absent from that snapshot.', 'small')
p('<b>Coverage.</b> The 40 mapped posts are selected evidence, not a representative sample. Several public-search pagination requests were blocked, leaving searches incomplete. A larger account-history collection was lost when the environment reset. The reported findings use the preserved, rechecked records.', 'small')
p('<b>Classification.</b> One reader coded the selected posts; there was no independent second coder. The chart\'s identity labels and original toxicity scores have not been independently validated. Allegation posts establish that accusations were made; this report makes no finding that the accusations are true.', 'small')
p('<b>What a numerical answer needs.</b> To measure how much the broader conduct explains the gap, a new analysis needs the original account/post mapping and comparable pre-decision histories for blocked and unblocked accounts. It must separate initial imports from incoming blocks and code the broader conduct consistently. The preserved mapping archive includes account IDs, post links, timestamps, hashes and the coding notes needed to inspect the selected evidence.', 'small')
heading('Primary sources')
refs = [
    ('Published audit and embedded chart data', ARTIFACT),
    ('Aaron\'s investigation / accidental-like explanation, 6 October 2025', aaron('3m2kgo3c3bk2u')),
    ('Autoblocker announcement, 30 September 2026', aaron('3mwqe37envs2x')),
    ('Initial-list clarification, 30 September 2026', aaron('3mwqeidhoo22w')),
    ('Sitewide-query explanation, 1 October 2026', aaron('3mwsv6uvlrc27')),
    ('Identity / incoming-interaction statement, 1 October 2026', aaron('3mwsv6uvvjs27')),
    ('Link to the example sample, 1 October 2026', aaron('3mwsv6uvxic27')),
    ('Public 50-interaction sample', SOURCE_SHEET),
    ('Toxicity classifier model card', 'https://huggingface.co/unitary/unbiased-toxic-roberta'),
    ('AT Protocol repository specification', 'https://atproto.com/specs/repository'),
]
for i, (label, url) in enumerate(refs, 1):
    p(f'{i}. ' + link(label, url), 'small')
p('The source-linked evidence is supplied in account_post_mapping.zip and autoblock_analysis_materials.zip. Decoded chart rows and their numerical reproduction are also supplied in recovered_autoblock_data.zip.', 'small')


# Independent contribution, with independently checked data and explicit credit.
page()
heading('Independent analysis: Michael Paulauski')
p('Michael Paulauski (' + link('@mike10010100.com', 'https://bsky.app/profile/mike10010100.com/post/3mxrorcrzjv23') + ') is an independent analyst and <b>is not a member of Friendly Society of Corvids</b>. He identified further checks of the published chart and classifier. The society evaluated his public analysis against the preserved chart data and primary posts.')
p('<b>The comparison group contains distinct profile categories.</b> Its pronoun-only category, with no detected trans marker, has a different recorded blocking rate from the category with neither feature. These are audit-defined flags whose identity validity has not been independently checked; the rates do not establish discrimination or the cause of blocking.')
rows = [['Audit-defined category', 'Blocked / accounts', 'Recorded rate']]
labels = {'explicit_trans_marker': 'Explicit trans marker', 'other_trans_signal': 'Other trans signal', 'pronouns_only': 'Pronouns, no detected trans marker', 'neither_marker_nor_pronouns': 'Neither detected trans marker nor pronouns'}
for key, label in labels.items():
    g = EXTERNAL['groups'][key]
    rows.append([label, f"{g['blocked']} / {g['accounts']}", f"{100*g['rate']:.1f}%"])
table(rows, [280, 123, 113])
p('The four categories exhaust all 1,678 decoded rows. Mike\'s subgroup counts and rounded rates reproduce exactly. The pronoun-only comparison gives a crude odds ratio of 2.164. Our specified band-adjusted model gives 2.126 (95% interval 1.634-2.765; p = 1.93 x 10^-8), close to his reported 2.11. His exact model specification was not supplied.', 'small')
p('<b>The date windows change the comparison population.</b> The all-year window contains 466 accounts absent from the recent window. Of the 395 additional unblocked accounts, 390 (98.7%) lack the author\'s explicit trans marker. This verifies a change in sample composition. Subtracting individual toxicity-band cells cannot uniquely identify earlier-only accounts because a shared account can change bands between date windows.')
p('<b>The live-only result does not support the combined headline.</b> The chart\'s live-only sample has 413 accounts, including 30 with the explicit marker and 13 of those blocked. Its precomputed model reports OR 1.70, 95% interval 0.76-3.78, p = 0.196. This does not statistically establish a live-only group difference, and the interval remains wide.')
p('Mike corrected his original N=674 and lowest-band figures in a ' + link('later post', 'https://bsky.app/profile/mike10010100.com/post/3mxru63thls26') + '. We use the corrected N=413. The lower observed marker-group rate is in the next-lowest band: 1/5 versus 13/42. The lowest band is 3/11 versus 41/224.', 'small')

page()
heading('Classifier and source-context checks')
if MODEL_CHECK:
    p('<b>The generic classifier gives low scores to context-sensitive strings.</b> The society independently ran Mike\'s four example strings through the named Hugging Face model at a fixed revision. All four fall below the audit\'s 0.02 cutoff. A low score does not establish that an interaction is harmless or equivalent in context to another interaction.')
    rows = [['Classifier test string (no factual endorsement)', 'Independent toxicity score']]
    for example in MODEL_CHECK['examples']:
        rows.append([html.escape(example['text']), f"{example['independent_score']:.6f}"])
    table(rows, [346, 170])
    p('Model: unitary/unbiased-toxic-roberta; revision ' + MODEL_CHECK['revision'] + '. CPU evaluation with sigmoid of the toxicity output. Three of Mike\'s rounded scores reproduce; the fourth is 0.000628 in our run versus his reported 0.00191. All four fall in the lowest band. This run verifies the supplied strings\' scores; it does not establish their membership in the author\'s anonymous sample.', 'small')
else:
    p('Mike reported very low classifier scores for context-sensitive strings. An independent model run is pending; the exact scores are not presented as verified here.')
p('<b>Name searches miss role-based targeting.</b> We retrieved again two previously verified posts referring to the head of Trust &amp; Safety using harm-related language. Neither contains Aaron or Roderick, and both precede their authors\' third-bulk blocks. They confirm the name-search blind spot Mike identified. The anonymous chart does not identify the members of its 178-account no-contact cohort, so exact membership in that cohort cannot be independently checked.')
p('The chart lists 178 no-contact cases across the three bulk loads: 15 + 72 + 91. The third load alone contains 91. We do not repeat the thread\'s description of all 178 as third-load cases.', 'small')
p('<b>The audit author has clarified her presentation.</b> In a ' + link('public update', 'https://bsky.app/profile/aidap.bsky.social/post/3mxrulsvkqk2u') + ', she says her opener made the result sound like it came from the bot. She separately ' + link('identifies the generic harshness measure as the weaker part', 'https://bsky.app/profile/aidap.bsky.social/post/3mxrulsvkql2u') + '. We verified these statements from the primary post records.')
p('Mike\'s claimed two identity-label errors in a 25-profile check, full membership of the no-contact cohort, and the share of blocks attributable to particular backlash events remain outside our verified findings. The source and correction notes distinguish these from the reproduced counts and scores.', 'small')
p('Independent source: ' + link('Michael Paulauski\'s analysis thread', 'https://bsky.app/profile/mike10010100.com/post/3mxrorcrzjv23') + '. Reproduction: scripts/check_mike_analysis.py and scripts/check_toxicity_examples.py. Results and source metadata are in analysis/data/.', 'small')

def footer(canvas, doc):
    canvas.setStrokeColor(colors.HexColor('#ddd8d0'))
    canvas.line(48, 38, 564, 38)
    canvas.setFont('ReportSans', 7.5)
    canvas.setFillColor(colors.HexColor('#666666'))
    canvas.drawString(48, 25, 'Friendly Society of Corvids | Autoblock methodology review | 13 October 2026')
    canvas.drawRightString(564, 25, str(doc.page))

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=48, rightMargin=48, topMargin=44, bottomMargin=50,
                        title='Autoblock Audit: What the evidence shows', author='Friendly Society of Corvids',
                        subject='Plain-language review with verified independent analysis credited to Michael Paulauski, a non-member')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
