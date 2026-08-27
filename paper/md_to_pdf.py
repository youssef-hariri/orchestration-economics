#!/usr/bin/env python3
"""
Convert the paper draft markdown to PDF with figures.
Uses markdown -> HTML -> weasyprint pipeline.
"""
import os
import re
import markdown
from weasyprint import HTML, CSS
from pathlib import Path

# Configuration
PAPER_DIR = Path("research/orchestration-economics/paper")
MD_FILE = PAPER_DIR / "FULL-PAPER-DRAFT.md"
OUTPUT_PDF = PAPER_DIR / "FULL-PAPER-DRAFT.pdf"

# Read markdown
with open(MD_FILE, 'r', encoding='utf-8') as f:
    md_text = f.read()

# Pre-process: fix figure paths to be absolute
# Markdown images: ![caption](figures/figX.png)
def fix_image_paths(text):
    def replace_img(match):
        alt = match.group(1)
        path = match.group(2)
        if not path.startswith('/'):
            abs_path = str((PAPER_DIR / path).resolve())
            return f'![{alt}]({abs_path})'
        return match.group(0)
    return re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img, text)

md_text = fix_image_paths(md_text)

# Convert markdown to HTML
md = markdown.Markdown(extensions=[
    'tables',
    'fenced_code',
    'toc',
    'nl2br',
])
html_body = md.convert(md_text)

# Build full HTML document with academic CSS
html_doc = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>The Economics of Orchestration</title>
<style>
@page {{
    size: A4;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @top-center {{
        content: string(doctitle);
        font-size: 9pt;
        color: #666;
        font-style: italic;
    }}
    @bottom-center {{
        content: counter(page);
        font-size: 10pt;
    }}
}}

body {{
    font-family: "Times New Roman", "DejaVu Serif", Georgia, serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #222;
    max-width: 100%;
}}

h1 {{
    font-size: 18pt;
    font-weight: bold;
    text-align: center;
    margin-top: 0;
    margin-bottom: 0.5em;
    string-set: doctitle content();
    page-break-before: always;
}}
h1:first-of-type {{
    page-break-before: auto;
}}

h2 {{
    font-size: 14pt;
    font-weight: bold;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
    color: #000;
    border-bottom: 1pt solid #ccc;
    padding-bottom: 0.2em;
    page-break-after: avoid;
}}

h3 {{
    font-size: 12pt;
    font-weight: bold;
    margin-top: 1.2em;
    margin-bottom: 0.4em;
    color: #222;
    page-break-after: avoid;
}}

h4 {{
    font-size: 11pt;
    font-weight: bold;
    font-style: italic;
    margin-top: 1em;
    margin-bottom: 0.3em;
    page-break-after: avoid;
}}

p {{
    margin: 0.6em 0;
    text-align: justify;
    orphans: 2;
    widows: 2;
}}

strong {{
    font-weight: bold;
}}

em {{
    font-style: italic;
}}

table {{
    border-collapse: collapse;
    width: 100%;
    margin: 1em 0;
    font-size: 10pt;
    page-break-inside: avoid;
}}

th, td {{
    border: 1pt solid #999;
    padding: 6pt 8pt;
    text-align: left;
    vertical-align: top;
}}

th {{
    background: #f0f0f0;
    font-weight: bold;
}}

tr:nth-child(even) {{
    background: #fafafa;
}}

img {{
    max-width: 100%;
    height: auto;
    display: block;
    margin: 1em auto;
}}

figure {{
    margin: 1.5em 0;
    page-break-inside: avoid;
    text-align: center;
}}

figcaption {{
    font-size: 10pt;
    font-style: italic;
    color: #444;
    margin-top: 0.5em;
    text-align: center;
}}

pre {{
    background: #f5f5f5;
    border: 1pt solid #ddd;
    border-radius: 3pt;
    padding: 10pt;
    overflow-x: auto;
    font-family: "Courier New", Consolas, monospace;
    font-size: 9pt;
    line-height: 1.4;
    page-break-inside: avoid;
    white-space: pre-wrap;
    word-wrap: break-word;
}}

code {{
    font-family: "Courier New", Consolas, monospace;
    font-size: 9.5pt;
    background: #f5f5f5;
    padding: 1pt 3pt;
    border-radius: 2pt;
}}

pre code {{
    background: none;
    padding: 0;
}}

blockquote {{
    margin: 1em 0;
    padding: 0.5em 1em;
    border-left: 3pt solid #ccc;
    background: #f9f9f9;
    font-style: italic;
    color: #555;
}}

ul, ol {{
    margin: 0.5em 0;
    padding-left: 2em;
}}

li {{
    margin: 0.2em 0;
}}

hr {{
    border: none;
    border-top: 1pt solid #ccc;
    margin: 1.5em 0;
}}

a {{
    color: #2E86AB;
    text-decoration: none;
}}

/* Abstract styling */
.abstract {{
    margin: 1em 2em;
    padding: 1em;
    background: #f9f9f9;
    border: 1pt solid #ddd;
    font-size: 10.5pt;
}}

/* Keywords */
.keywords {{
    font-size: 10pt;
    margin: 0.5em 2em;
    color: #444;
}}

/* Section break */
.section-break {{
    page-break-before: always;
}}

/* Prevent orphans in lists */
li {{
    orphans: 2;
    widows: 2;
}}
</style>
</head>
<body>
{html_body}
</body>
</html>
'''

# Write HTML for debugging
html_file = PAPER_DIR / "FULL-PAPER-DRAFT.html"
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_doc)

# Convert to PDF
print("Converting to PDF...")
doc = HTML(string=html_doc, base_url=str(PAPER_DIR))
doc.write_pdf(str(OUTPUT_PDF))

print(f"PDF generated: {OUTPUT_PDF}")
print(f"HTML generated: {html_file}")
print(f"File size: {OUTPUT_PDF.stat().st_size / 1024 / 1024:.1f} MB")
