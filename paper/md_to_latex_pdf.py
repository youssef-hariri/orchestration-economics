#!/usr/bin/env python3
"""
Convert markdown paper draft to LaTeX and compile to PDF.
Uses xelatex for compilation.
"""
import os
import re
import subprocess
from pathlib import Path

PAPER_DIR = Path("research/orchestration-economics/paper")
MD_FILE = PAPER_DIR / "FULL-PAPER-DRAFT.md"
TEX_FILE = PAPER_DIR / "FULL-PAPER-DRAFT.tex"
PDF_FILE = PAPER_DIR / "FULL-PAPER-DRAFT.pdf"

def escape_latex(text):
    """Escape special LaTeX characters."""
    # Order matters: backslash first
    replacements = [
        ('\\', '\\textbackslash{}'),
        ('&', '\\&'),
        ('%', '\\%'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('_', '\\_'),
        ('{', '\\{'),
        ('}', '\\}'),
        ('~', '\\textasciitilde{}'),
        ('^', '\\textasciicircum{}'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text

def convert_inline(text):
    """Convert inline markdown to LaTeX."""
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    # Inline code
    text = re.sub(r'`(.*?)`', r'\\texttt{\1}', text)
    # Links [text](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\\href{\2}{\1}', text)
    return text

def parse_table(lines, start_idx):
    """Parse a markdown table and return LaTeX + next index."""
    rows = []
    i = start_idx
    while i < len(lines) and lines[i].startswith('|'):
        rows.append(lines[i])
        i += 1
    
    if len(rows) < 2:
        return None, start_idx + 1
    
    # Skip separator row (row 1)
    data_rows = [rows[0]] + rows[2:]
    
    # Parse each row
    def parse_row(row):
        cells = [c.strip() for c in row.strip('|').split('|')]
        return cells
    
    headers = parse_row(data_rows[0])
    body = [parse_row(r) for r in data_rows[1:]]
    
    num_cols = len(headers)
    col_spec = 'l' * num_cols
    
    latex = '\\begin{table}[htbp]\n\\centering\n\\begin{tabular}{' + col_spec + '}\n\\toprule\n'
    latex += ' & '.join(escape_latex(convert_inline(h)) for h in headers) + ' \\\\\n'
    latex += '\\midrule\n'
    for row in body:
        # Pad if needed
        while len(row) < num_cols:
            row.append('')
        latex += ' & '.join(escape_latex(convert_inline(c)) for c in row[:num_cols]) + ' \\\\\n'
    latex += '\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    
    return latex, i

def convert_markdown_to_latex(md_text):
    """Convert full markdown to LaTeX body."""
    lines = md_text.split('\n')
    latex_lines = []
    i = 0
    in_code_block = False
    code_lang = None
    code_lines = []
    in_list = False
    list_type = None
    
    while i < len(lines):
        line = lines[i]
        
        # Code blocks
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_lang = line[3:].strip()
                code_lines = []
            else:
                in_code_block = False
                code_content = '\n'.join(code_lines)
                latex_lines.append('\\begin{verbatim}')
                latex_lines.append(code_content)
                latex_lines.append('\\end{verbatim}\n')
            i += 1
            continue
        
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue
        
        # Empty line
        if line.strip() == '':
            if in_list:
                if list_type == 'ul':
                    latex_lines.append('\\end{itemize}\n')
                else:
                    latex_lines.append('\\end{enumerate}\n')
                in_list = False
                list_type = None
            latex_lines.append('')
            i += 1
            continue
        
        # Tables
        if line.startswith('|') and '|' in line[1:]:
            table_latex, i = parse_table(lines, i)
            if table_latex:
                latex_lines.append(table_latex)
            continue
        
        # Headers
        if line.startswith('# '):
            text = line[2:].strip()
            latex_lines.append(f'\\section{{{escape_latex(convert_inline(text))}}}')
            i += 1
            continue
        if line.startswith('## '):
            text = line[3:].strip()
            latex_lines.append(f'\\subsection{{{escape_latex(convert_inline(text))}}}')
            i += 1
            continue
        if line.startswith('### '):
            text = line[4:].strip()
            latex_lines.append(f'\\subsubsection{{{escape_latex(convert_inline(text))}}}')
            i += 1
            continue
        if line.startswith('#### '):
            text = line[5:].strip()
            latex_lines.append(f'\\paragraph{{{escape_latex(convert_inline(text))}}}')
            i += 1
            continue
        
        # Horizontal rule
        if line.strip() == '---':
            latex_lines.append('\\hrule\n')
            i += 1
            continue
        
        # Blockquote
        if line.startswith('> '):
            text = line[2:].strip()
            latex_lines.append('\\begin{quote}')
            latex_lines.append(escape_latex(convert_inline(text)))
            latex_lines.append('\\end{quote}\n')
            i += 1
            continue
        
        # Lists
        if line.startswith('- '):
            if not in_list or list_type != 'ul':
                if in_list:
                    if list_type == 'ol':
                        latex_lines.append('\\end{enumerate}\n')
                latex_lines.append('\\begin{itemize}')
                in_list = True
                list_type = 'ul'
            text = line[2:].strip()
            latex_lines.append(f'\\item {escape_latex(convert_inline(text))}')
            i += 1
            continue
        
        if re.match(r'^\d+\.\s', line):
            if not in_list or list_type != 'ol':
                if in_list:
                    if list_type == 'ul':
                        latex_lines.append('\\end{itemize}\n')
                latex_lines.append('\\begin{enumerate}')
                in_list = True
                list_type = 'ol'
            text = re.sub(r'^\d+\.\s', '', line).strip()
            latex_lines.append(f'\\item {escape_latex(convert_inline(text))}')
            i += 1
            continue
        
        # Images
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if img_match:
            caption = img_match.group(1)
            path = img_match.group(2)
            # Make path absolute if relative
            if not path.startswith('/'):
                path = str((PAPER_DIR / path).resolve())
            # Use PNG for PDF inclusion
            path_png = path
            if path.endswith('.pdf'):
                path_png = path[:-4] + '.png'
            latex_lines.append('\\begin{figure}[htbp]')
            latex_lines.append('\\centering')
            latex_lines.append(f'\\includegraphics[width=\\textwidth]{{{path_png}}}')
            latex_lines.append(f'\\caption{{{escape_latex(convert_inline(caption))}}}')
            latex_lines.append('\\end{figure}\n')
            i += 1
            continue
        
        # Regular paragraph
        text = convert_inline(line)
        # Convert subscripts like BF₁₀, p_FDR
        text = re.sub(r'(_)([a-zA-Z0-9]+)', r'\\textsubscript{\2}', text)
        latex_lines.append(escape_latex(text))
        i += 1
    
    if in_list:
        if list_type == 'ul':
            latex_lines.append('\\end{itemize}\n')
        else:
            latex_lines.append('\\end{enumerate}\n')
    
    return '\n'.join(latex_lines)

# Read markdown
with open(MD_FILE, 'r', encoding='utf-8') as f:
    md_text = f.read()

latex_body = convert_markdown_to_latex(md_text)

# Build full LaTeX document
latex_doc = r'''\documentclass[11pt,a4paper]{article}

% Packages
\usepackage{fontspec}
\usepackage{geometry}
\geometry{margin=2.5cm}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{hyperref}
\usepackage{enumitem}
\usepackage{fancyhdr}
\usepackage{lastpage}
\usepackage{xcolor}
\usepackage{verbatim}
\usepackage{caption}
\usepackage{subcaption}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{setspace}

% Page setup
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\textit{The Economics of Orchestration}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}

% Hyperref setup
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=blue,
    citecolor=blue,
}

\begin{document}

''' + latex_body + r'''

\end{document}
'''

# Write .tex file
with open(TEX_FILE, 'w', encoding='utf-8') as f:
    f.write(latex_doc)

print(f"LaTeX written: {TEX_FILE}")

# Compile with xelatex (run twice for references)
print("Compiling with xelatex (pass 1/2)...")
result = subprocess.run(
    ['xelatex', '-interaction=nonstopmode', str(TEX_FILE.name)],
    capture_output=True, text=True, cwd=str(PAPER_DIR)
)
if result.returncode != 0:
    print("xelatex warnings/errors:")
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)

print("Compiling with xelatex (pass 2/2)...")
result = subprocess.run(
    ['xelatex', '-interaction=nonstopmode', str(TEX_FILE.name)],
    capture_output=True, text=True, cwd=str(PAPER_DIR)
)
print("Compiling with xelatex (pass 1/2)...")
result = subprocess.run(
    ['xelatex', '-interaction=nonstopmode', '-output-directory', str(PAPER_DIR), str(TEX_FILE)],
    capture_output=True, text=True, cwd=str(PAPER_DIR)
)
if result.returncode != 0:
    print("xelatex warnings/errors:")
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    print(result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)

print("Compiling with xelatex (pass 2/2)...")
result = subprocess.run(
    ['xelatex', '-interaction=nonstopmode', '-output-directory', str(PAPER_DIR), str(TEX_FILE)],
    capture_output=True, text=True, cwd=str(PAPER_DIR)
)

if PDF_FILE.exists():
    size_mb = PDF_FILE.stat().st_size / 1024 / 1024
    print(f"PDF generated: {PDF_FILE}")
    print(f"File size: {size_mb:.1f} MB")
else:
    print("PDF generation failed!")
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
