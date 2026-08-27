#!/usr/bin/env python3
"""
Convert the business version markdown to LaTeX only (no PDF compilation).
Order: escape raw LaTeX chars FIRST, then convert markdown formatting to LaTeX commands.
"""
import re
from pathlib import Path

PAPER_DIR = Path("research/orchestration-economics/paper")
SRC = PAPER_DIR / "FULL-PAPER-DRAFT-BUSINESS-v3.md"
DST = PAPER_DIR / "FULL-PAPER-DRAFT-BUSINESS-v3.tex"

def escape_latex(text):
    """Escape special LaTeX characters in raw markdown text."""
    replacements = [
        ('&', '\\&'),
        ('%', '\\%'),
        ('$', '\\$'),
        ('#', '\\#'),
        ('_', '\\_'),
        ('~', '\\textasciitilde{}'),
        ('^', '\\textasciicircum{}'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    text = text.replace('{', '\\{')
    text = text.replace('}', '\\}')
    return text

def convert_inline(text):
    """Convert markdown inline formatting to LaTeX commands."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    text = re.sub(r'`(.*?)`', r'\\texttt{\1}', text)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\\href{\2}{\1}', text)
    return text

def process_text(text):
    """Escape then convert inline formatting."""
    return convert_inline(escape_latex(text))

def parse_table(lines, start_idx):
    rows = []
    i = start_idx
    while i < len(lines) and lines[i].startswith('|'):
        rows.append(lines[i])
        i += 1
    if len(rows) < 2:
        return None, start_idx + 1
    data_rows = [rows[0]] + rows[2:]
    def parse_row(row):
        cells = [c.strip() for c in row.strip('|').split('|')]
        return cells
    headers = parse_row(data_rows[0])
    body = [parse_row(r) for r in data_rows[1:]]
    num_cols = len(headers)
    col_spec = 'l' * num_cols
    latex = '\\begin{table}[htbp]\n\\centering\n\\begin{tabular}{' + col_spec + '}\n\\toprule\n'
    row_end = ' \\\\\n'
    latex += ' & '.join(process_text(h) for h in headers) + row_end
    latex += '\\midrule\n'
    for row in body:
        while len(row) < num_cols:
            row.append('')
        latex += ' & '.join(process_text(c) for c in row[:num_cols]) + row_end
    latex += '\\bottomrule\n\\end{tabular}\n\\end{table}\n'
    return latex, i

def convert_markdown_to_latex(md_text):
    lines = md_text.split('\n')
    latex_lines = []
    i = 0
    in_code_block = False
    code_lines = []
    in_list = False
    list_type = None
    
    while i < len(lines):
        line = lines[i]
        
        if line.startswith('```'):
            if not in_code_block:
                in_code_block = True
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
        
        if line.startswith('|') and '|' in line[1:]:
            table_latex, i = parse_table(lines, i)
            if table_latex:
                latex_lines.append(table_latex)
            continue
        
        if line.startswith('# '):
            text = line[2:].strip()
            latex_lines.append(f'\\section{{{process_text(text)}}}')
            i += 1
            continue
        if line.startswith('## '):
            text = line[3:].strip()
            latex_lines.append(f'\\subsection{{{process_text(text)}}}')
            i += 1
            continue
        if line.startswith('### '):
            text = line[4:].strip()
            latex_lines.append(f'\\subsubsection{{{process_text(text)}}}')
            i += 1
            continue
        if line.startswith('#### '):
            text = line[5:].strip()
            latex_lines.append(f'\\paragraph{{{process_text(text)}}}')
            i += 1
            continue
        
        if line.strip() == '---':
            latex_lines.append('\\hrule\n')
            i += 1
            continue
        
        if line.startswith('> '):
            text = line[2:].strip()
            latex_lines.append('\\begin{quote}')
            latex_lines.append(process_text(text))
            latex_lines.append('\\end{quote}\n')
            i += 1
            continue
        
        if line.startswith('- '):
            if not in_list or list_type != 'ul':
                if in_list:
                    if list_type == 'ol':
                        latex_lines.append('\\end{enumerate}\n')
                latex_lines.append('\\begin{itemize}')
                in_list = True
                list_type = 'ul'
            text = line[2:].strip()
            latex_lines.append(f'\\item {process_text(text)}')
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
            latex_lines.append(f'\\item {process_text(text)}')
            i += 1
            continue
        
        img_match = re.match(r'^!\[(.*?)\]\((.*?)\)$', line.strip())
        if img_match:
            caption = img_match.group(1)
            path = img_match.group(2)
            if not path.startswith('/'):
                path = str((PAPER_DIR / path).resolve())
            path_png = path
            if path.endswith('.pdf'):
                path_png = path[:-4] + '.png'
            latex_lines.append('\\begin{figure}[htbp]')
            latex_lines.append('\\centering')
            latex_lines.append(f'\\includegraphics[width=\\textwidth]{{{path_png}}}')
            latex_lines.append(f'\\caption{{{process_text(caption)}}}')
            latex_lines.append('\\end{figure}\n')
            i += 1
            continue
        
        latex_lines.append(process_text(line))
        i += 1
    
    if in_list:
        if list_type == 'ul':
            latex_lines.append('\\end{itemize}\n')
        else:
            latex_lines.append('\\end{enumerate}\n')
    
    return '\n'.join(latex_lines)

with open(SRC, 'r', encoding='utf-8') as f:
    md_text = f.read()

latex_body = convert_markdown_to_latex(md_text)

latex_doc = r'''\documentclass[11pt,a4paper]{article}
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
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\textit{Orchestrate or Upgrade?}}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\hypersetup{colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue}
\begin{document}
''' + latex_body + r'''
\end{document}
'''

with open(DST, 'w', encoding='utf-8') as f:
    f.write(latex_doc)

print(f"LaTeX written: {DST}")
print(f"Size: {len(latex_doc):,} chars")
