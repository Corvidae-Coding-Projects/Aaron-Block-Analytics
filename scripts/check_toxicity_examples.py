"""Reproduce the toxicity-score examples identified by Michael Paulauski.

Compilation and verification: Friendly Society of Corvids.
Michael Paulauski is an independent contributor, not a society member.
This scores supplied text; it does not identify the source accounts.
"""
from pathlib import Path
import argparse
import hashlib
import json
import tempfile

import torch
import transformers
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL = 'unitary/unbiased-toxic-roberta'
REVISION = '36295dd80b422dc49f40052021430dae76241adc'
EXAMPLES = [
    ('Enjoy the camps Aaron', 0.00043),
    ('Enjoy the camps I guess', 0.00045),
    ('She was barely legal, Aaron', 0.00071),
    ('liked jailbait on his work account', 0.00191),
]

parser = argparse.ArgumentParser()
parser.add_argument('--cache-dir', type=Path, default=Path(tempfile.gettempdir()) / 'corvids_toxicity_model')
parser.add_argument('--output', type=Path)
args = parser.parse_args()
torch.set_num_threads(4)
tokenizer = AutoTokenizer.from_pretrained(MODEL, revision=REVISION, cache_dir=args.cache_dir, trust_remote_code=False)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, revision=REVISION, cache_dir=args.cache_dir, trust_remote_code=False)
model.eval()
tokens = tokenizer([s for s, _ in EXAMPLES], padding=True, truncation=True, max_length=512, return_tensors='pt')
label = next(int(i) for i, name in model.config.id2label.items() if name == 'toxicity')
with torch.no_grad():
    probabilities = torch.sigmoid(model(**tokens).logits)[:, label].tolist()
weights = list(args.cache_dir.rglob('pytorch_model.bin'))
result = {
    'verification_attribution': 'Friendly Society of Corvids',
    'example_source': 'Michael Paulauski (@mike10010100.com), independent non-member',
    'source_post_url': 'https://bsky.app/profile/mike10010100.com/post/3mxru62plmg2z',
    'model': MODEL,
    'revision': REVISION,
    'torch_version': torch.__version__,
    'transformers_version': transformers.__version__,
    'method': 'CPU inference in evaluation mode; sigmoid of toxicity logit; tokenization with truncation at 512 tokens',
    'weights_sha256': hashlib.sha256(weights[0].read_bytes()).hexdigest() if weights else None,
    'examples': [{'text': s, 'mike_reported_rounded_score': old, 'independent_score': score,
                  'below_0_02': score < 0.02} for (s, old), score in zip(EXAMPLES, probabilities)],
    'scope': 'Reproduces scores for the supplied strings. Does not verify original sample membership, account identity or exact original audit preprocessing.',
}
text = json.dumps(result, indent=2)
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text + '\n')
print(text)
