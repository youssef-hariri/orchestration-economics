"""Audit-only inventory. Never writes to the source manuscript or experiment files."""
import hashlib, json, re, shutil
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parent.parent
PAPER = ROOT / 'paper/P5_v14.3.tex'
text = PAPER.read_text()
lines = text.splitlines()
# Snapshot is an audit artifact, not a replacement draft.
shutil.copyfile(PAPER, OUT / 'manuscript_snapshot.tex')
manifest = []
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or OUT in p.parents or '.git' in p.parts or p.name == '.env' or p.name == '.DS_Store' or '__pycache__' in p.parts:
        continue
    s = p.stat()
    manifest.append({'path': str(p.relative_to(ROOT)), 'size': s.st_size, 'mtime_ns': s.st_mtime_ns})
(OUT / 'source_baseline.json').write_text(json.dumps({'paper_sha256': hashlib.sha256(PAPER.read_bytes()).hexdigest(), 'line_count': len(lines), 'files': manifest}, indent=2))
number = re.compile(r'(?<![A-Za-z])(?:[-+−]?\d+(?:\{,\}\d{3}|,\d{3})*(?:\.\d+)?)(?:\\%|%)?')
section = ''
inventory = []
for n, line in enumerate(lines, 1):
    s = line.strip()
    if re.match(r'\\(?:sub)*section', s):
        section = s
    if not s: kind = 'blank'
    elif s.startswith('%'): kind = 'comment'
    elif n < 61: kind = 'formatting/preamble'
    elif n >= 2299: kind = 'bibliography'
    elif re.match(r'^\\(?:begin|end|label|centering|smallskip|medskip|bigskip|toprule|midrule|bottomrule|footnotesize|small|normalsize|clearpage|appendix|maketitle|date|par\\vspace)', s): kind = 'layout/structure'
    elif re.match(r'^\\(?:sub)*section', s): kind = 'heading'
    else: kind = 'content'
    inventory.append({'line': n, 'section': section, 'kind': kind, 'text': line, 'numeric_tokens': number.findall(line) if kind in ('content','bibliography') else []})
(OUT / 'line_inventory.json').write_text(json.dumps(inventory, ensure_ascii=False, indent=2))
print(json.dumps({'lines': len(lines), 'content_lines': sum(x['kind']=='content' for x in inventory), 'numeric_content_lines': sum(bool(x['numeric_tokens']) and x['kind']=='content' for x in inventory), 'source_files': len(manifest), 'sha256': hashlib.sha256(PAPER.read_bytes()).hexdigest()}))
