# Compilation and analysis: Friendly Society of Corvids.
"""Fetch the explicitly published sample table; preserve text for local verification."""
import json,pathlib,urllib.request
from html.parser import HTMLParser
ROOT=pathlib.Path(__file__).resolve().parent
URL='https://docs.google.com/spreadsheets/d/e/2PACX-1vSqDngHpDnBvSvSxvxaJO4679WlwqfNBgPsX3qJMqWMHJlUmHlZ0siklD73gZI-5fTX1S6bpKB2ifdj/pubhtml/sheet?headers=false&gid=2014667266'
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  if tag in ('td','th') and self.row is not None:self.cell=[]
  if tag=='br' and self.cell is not None:self.cell.append('\n')
 def handle_data(self,data):
  if self.cell is not None:self.cell.append(data)
 def handle_endtag(self,tag):
  if tag in ('td','th') and self.cell is not None:self.row.append(''.join(self.cell));self.cell=None
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
with urllib.request.urlopen(URL,timeout=30) as response:body=response.read().decode()
p=Parser();p.feed(body)
assert len([r for r in p.rows if len(r)==2 and r[0].isdigit()])==50
(ROOT/'published_sample_rows.json').write_text(json.dumps(p.rows,ensure_ascii=False))
print('Recovered 50 published sample rows')
