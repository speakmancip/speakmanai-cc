"""
doc_writer.py — Convert a Markdown file to a branded document (HTML → PDF).

USAGE
  python doc_writer.py input.md [options]

OPTIONS
  --template  path/to/template/dir     Template directory containing logo.png
                                       (default: templates/default next to this script)
  --title     "Document Title"         (default: first H1 in markdown)
  --subtitle  "Type · Date · Source"   (default: auto-generated)
  --output    output_name              (default: input filename stem)
  --no-pdf                             Stop after HTML — skip PDF generation
  --yes                                Non-interactive: skip all confirmation prompts

TEMPLATE DIRECTORY
  A template directory must contain:
    logo.png    — Brand logo rendered in the document header

MARKDOWN CONVENTIONS
  # H1          → document title (first H1 only; use --title to override)
  ## H2         → major section with page break
  ### H3        → subsection
  #### H4       → sub-subsection
  ---           → divider
  **bold**      → <strong>
  `code`        → <code>
  Tables        → styled table
  - / * lists   → <ul>
  1. lists      → <ol>
  ```mermaid    → rendered Mermaid diagram
"""

import argparse
import base64
import re
import sys
import webbrowser
from datetime import date
import os
from pathlib import Path

import subprocess


# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

CSS = """
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Roboto Mono', monospace;
      font-size: 14px; line-height: 1.7; color: #1a1a1a;
      background: #ebebeb; padding: 32px 24px;
    }
    .page {
      max-width: 1100px; margin: 0 auto; background: #fff;
      border: 1px solid #ddd; border-radius: 4px; overflow: hidden;
    }
    .doc-header {
      background: #0a0a0a; color: #fff;
      padding: 24px 48px; display: flex; align-items: center;
      justify-content: space-between;
    }
    .doc-header img { height: 36px; }
    .doc-header .meta { text-align: right; font-size: 11px; color: #999; }
    .doc-header .meta .title { font-size: 16px; color: #fff; font-weight: 700; margin-bottom: 4px; }

    .toc { background: #fafafa; border-bottom: 1px solid #e8ecf0; padding: 18px 48px; }
    .toc h2 {
      font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em;
      color: #999; margin-bottom: 10px;
    }
    .toc ol { padding-left: 18px; column-count: 2; column-gap: 32px; }
    .toc li { font-size: 12px; margin-bottom: 4px; }
    .toc a { color: #1a1a1a; text-decoration: none; }
    .toc a:hover { color: #00c060; }

    .content { padding: 32px 48px 48px; }

    h2.section {
      background: #0a0a0a; color: #00ff7f;
      font-size: 13px; font-weight: 700; letter-spacing: 0.06em;
      text-transform: uppercase; padding: 8px 16px;
      margin: 40px -48px 24px; break-before: always;
    }
    h2.section:first-child { margin-top: 0; }

    h3 {
      font-size: 13px; font-weight: 700; color: #0a0a0a;
      border-left: 3px solid #00c060; padding: 4px 10px;
      margin: 24px 0 10px; background: #f7f9f7;
    }
    h4 {
      font-size: 12px; font-weight: 700; color: #333;
      margin: 18px 0 8px;
    }

    p { margin-bottom: 12px; }
    hr { border: none; border-top: 1px solid #e8ecf0; margin: 24px 0; }

    blockquote {
      border-left: 4px solid #f5a623; background: #fffdf5;
      padding: 10px 16px; margin: 16px 0; font-size: 13px; color: #7a5c00;
    }

    table {
      width: 100%; border-collapse: collapse;
      font-size: 12px; margin-bottom: 20px;
    }
    th {
      background: #0a0a0a; color: #00ff7f;
      font-size: 10px; font-weight: 700; text-transform: uppercase;
      letter-spacing: 0.06em; padding: 8px 10px; text-align: left;
    }
    td { padding: 7px 10px; border-bottom: 1px solid #eee; vertical-align: top; }
    tr:nth-child(even) td { background: #f9fafb; }
    tr:last-child td { border-bottom: none; }

    ul, ol { padding-left: 22px; margin-bottom: 12px; }
    li { margin-bottom: 4px; }

    code {
      font-family: 'Roboto Mono', monospace; font-size: 12px;
      background: #f3f4f6; padding: 1px 5px; border-radius: 3px; color: #c7254e;
    }

    .code-block {
      background: #111; border: 1px solid #2a2a2a; border-radius: 4px;
      padding: 12px 16px; margin-bottom: 14px; overflow-x: auto;
    }
    .code-block pre {
      margin: 0; font-family: 'Roboto Mono', monospace; font-size: 12px;
      color: #00ff7f; line-height: 1.6;
    }

    strong { font-weight: 700; }
    em { font-style: italic; }

    .doc-footer {
      background: #f5f5f5; border-top: 1px solid #e0e0e0;
      padding: 10px 48px; font-size: 10px; color: #999;
      display: flex; justify-content: space-between;
    }

    @media print {
      body { background: #fff; padding: 0; }
      .page { border: none; border-radius: 0; max-width: 100%; }
      .content { padding: 20px 40px 32px; }
      h2.section { break-before: always; page-break-before: always; font-size: 12px; padding: 7px 14px; }
      h2.section:first-of-type { break-before: avoid; page-break-before: avoid; }
      h2.section, h3, h4 { break-after: avoid; }
      h3 { font-size: 11px; padding: 5px 10px; margin: 16px 0 6px; }
      .toc { break-inside: avoid; }
      table { break-inside: auto; }
      tr { break-inside: avoid; }
    }
"""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{page_title}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({{startOnLoad:true, theme:'default'}});</script>
  <style>
{css}
  </style>
</head>
<body>
<div class="page">
  <div class="doc-header">
    <img src="{logo}" alt="Logo" />
    <div class="meta">
      <div class="title">{doc_title}</div>
      <div>{subtitle}</div>
    </div>
  </div>
  <div class="toc">
    <h2>Table of Contents</h2>
    <ol>
{toc_items}
    </ol>
  </div>
  <div class="content">
{body}
  </div>
  <div class="doc-footer">
    <span>{doc_title}</span>
    <span>{subtitle}</span>
  </div>
</div>
</body>
</html>
"""


# ─────────────────────────────────────────────────────────────────────────────
# INLINE RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def inline(text: str) -> str:
    """Convert inline Markdown to HTML."""
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
    return text


# ─────────────────────────────────────────────────────────────────────────────
# TABLE PARSER
# ─────────────────────────────────────────────────────────────────────────────

def parse_table(rows: list) -> str:
    out = ['    <table>\n']
    header_done = False
    for row in rows:
        cells = [c.strip() for c in row.strip().strip('|').split('|')]
        if all(re.match(r'^[-: ]+$', c) for c in cells):
            header_done = True
            continue
        tag = 'th' if not header_done else 'td'
        out.append('      <tr>' + ''.join(f'<{tag}>{inline(c)}</{tag}>' for c in cells) + '</tr>\n')
        if not header_done:
            header_done = True
    out.append('    </table>\n')
    return ''.join(out)


# ─────────────────────────────────────────────────────────────────────────────
# MARKDOWN → HTML
# ─────────────────────────────────────────────────────────────────────────────

def md_to_html(md_text: str):
    lines = md_text.splitlines()
    output = []
    doc_title = None
    toc_sections = []
    section_count = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # H1 — document title
        if line.startswith('# ') and not doc_title:
            doc_title = line[2:].strip()
            i += 1
            continue

        # H2 — major section
        if line.startswith('## '):
            section_count += 1
            sid = f's{section_count}'
            label = line[3:].strip()
            toc_sections.append((sid, label))
            output.append(f'    <h2 class="section" id="{sid}">{inline(label)}</h2>\n')
            i += 1
            continue

        # H3
        if line.startswith('### '):
            output.append(f'    <h3>{inline(line[4:].strip())}</h3>\n')
            i += 1
            continue

        # H4
        if line.startswith('#### '):
            output.append(f'    <h4>{inline(line[5:].strip())}</h4>\n')
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^-{3,}$', line.strip()):
            output.append('    <hr />\n')
            i += 1
            continue

        # Fenced code block
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip().lower()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_content = '\n'.join(code_lines)
            if lang == 'mermaid':
                escaped = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                output.append(f'    <div class="mermaid">{escaped}</div>\n')
            else:
                escaped = code_content.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                output.append(f'    <div class="code-block"><pre>{escaped}</pre></div>\n')
            i += 1
            continue

        # Table
        if '|' in line and line.strip().startswith('|'):
            table_rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip().startswith('|'):
                table_rows.append(lines[i])
                i += 1
            output.append(parse_table(table_rows))
            continue

        # Unordered list
        if re.match(r'^[-*+]\s', line):
            output.append('    <ul>\n')
            while i < len(lines) and re.match(r'^[-*+]\s', lines[i]):
                output.append(f'      <li>{inline(lines[i][2:].strip())}</li>\n')
                i += 1
            output.append('    </ul>\n')
            continue

        # Ordered list
        if re.match(r'^\d+\.\s', line):
            output.append('    <ol>\n')
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i]):
                output.append(f'      <li>{inline(re.sub(r"^\d+\.\s", "", lines[i]))}</li>\n')
                i += 1
            output.append('    </ol>\n')
            continue

        # Blockquote
        if line.startswith('> '):
            bq_lines = []
            while i < len(lines) and lines[i].startswith('> '):
                bq_lines.append(inline(lines[i][2:]))
                i += 1
            output.append(f'    <blockquote>{" ".join(bq_lines)}</blockquote>\n')
            continue

        # Blank line
        if not line.strip():
            i += 1
            continue

        # Paragraph
        output.append(f'    <p>{inline(line.strip())}</p>\n')
        i += 1

    return doc_title, ''.join(output), toc_sections


# ─────────────────────────────────────────────────────────────────────────────
# HTML BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def build_html(doc_title, subtitle, body_html, toc_sections, logo_b64, page_title):
    toc_items = '\n'.join(
        f'      <li><a href="#{sid}">{label}</a></li>'
        for sid, label in toc_sections
    )
    return HTML_TEMPLATE.format(
        page_title=page_title,
        css=CSS,
        logo=logo_b64,
        doc_title=doc_title,
        subtitle=subtitle,
        toc_items=toc_items,
        body=body_html,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_pdf(html_path: Path, pdf_path: Path):
    """Try puppeteer via Node, then pyppeteer, then warn."""
    # Try Node + puppeteer (most common in this project's environment)
    node_script = f"""
const puppeteer = require('puppeteer');
(async () => {{
  const browser = await puppeteer.launch({{headless: 'new'}});
  const page = await browser.newPage();
  await page.goto('file:///{html_path.resolve().as_posix()}', {{waitUntil: 'networkidle0'}});
  await page.pdf({{
    path: '{pdf_path.resolve().as_posix()}',
    format: 'A4',
    margin: {{top: '10mm', bottom: '10mm', left: '10mm', right: '10mm'}},
    printBackground: true
  }});
  await browser.close();
}})();
"""
    node_script_path = html_path.parent / '_pdf_gen.js'
    node_modules = Path(__file__).parent.parent / 'node_modules'

    try:
        node_script_path.write_text(node_script, encoding='utf-8')
        result = subprocess.run(
            ['node', str(node_script_path)],
            capture_output=True, text=True,
            env={**os.environ, 'NODE_PATH': str(node_modules)}
        )
        node_script_path.unlink(missing_ok=True)
        if result.returncode == 0 and pdf_path.exists():
            return True
        print(f'  Node PDF warning: {result.stderr[:200]}')
    except Exception as e:
        node_script_path.unlink(missing_ok=True)
        print(f'  Node PDF unavailable: {e}')

    print('  PDF generation skipped — install puppeteer (npm install puppeteer) to enable.')
    return False


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # Resolve default template dir relative to this script
    script_dir = Path(__file__).parent
    default_template = script_dir.parent / 'templates' / 'default'

    parser = argparse.ArgumentParser(description='Branded Markdown → HTML/PDF document writer')
    parser.add_argument('input',       help='Input markdown file')
    parser.add_argument('--template',  default=str(default_template), help='Template directory (must contain logo.png)')
    parser.add_argument('--title',     help='Document title (overrides first H1)')
    parser.add_argument('--subtitle',  help='Document subtitle')
    parser.add_argument('--output',    help='Output file stem (no extension)')
    parser.add_argument('--no-pdf',    action='store_true', help='Stop after HTML')
    parser.add_argument('--yes',       action='store_true', help='Non-interactive: skip all prompts')
    args = parser.parse_args()

    input_path   = Path(args.input)
    template_dir = Path(args.template)
    logo_path    = template_dir / 'logo.png'
    today        = date.today().isoformat()

    if not input_path.exists():
        print(f'ERROR: {input_path} not found.')
        sys.exit(1)

    stem      = args.output or input_path.stem
    html_path = input_path.parent / f'{stem}.html'
    pdf_path  = input_path.parent / f'{stem}.pdf'

    # Load logo
    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            logo_b64 = 'data:image/png;base64,' + base64.b64encode(f.read()).decode()
    else:
        print(f'WARNING: logo not found at {logo_path}')
        logo_b64 = ''

    # Parse markdown
    md_text = input_path.read_text(encoding='utf-8')
    parsed_title, body_html, toc_sections = md_to_html(md_text)

    doc_title    = args.title    or parsed_title or stem
    doc_subtitle = args.subtitle or f'Generated {today}'

    # Summary
    sep = '-' * 60
    print(sep)
    print(f'  Input     : {input_path}')
    print(f'  Template  : {template_dir}')
    print(f'  Title     : {doc_title}')
    print(f'  Sections  : {len(toc_sections)}')
    for sid, label in toc_sections:
        print(f'              #{sid}  {label}')
    print(f'  Output    : {html_path}')
    print(sep)

    if not args.yes:
        raw = input('\nBuild HTML? [Y/n]: ').strip().lower()
        if raw not in ('', 'y', 'yes'):
            print('Aborted.')
            sys.exit(0)

    # Build HTML
    html = build_html(doc_title, doc_subtitle, body_html, toc_sections, logo_b64, doc_title)
    html_path.write_text(html, encoding='utf-8')
    size_kb = html_path.stat().st_size // 1024
    print(f'\n  HTML written → {html_path} ({size_kb} KB)')

    if args.no_pdf:
        return

    if not args.yes:
        webbrowser.open(html_path.resolve().as_uri())
        input('\nReview in browser. Press Enter to generate PDF...')

    # Build PDF
    print('\n  Generating PDF...')
    success = generate_pdf(html_path, pdf_path)
    if success:
        size_kb = pdf_path.stat().st_size // 1024
        print(f'  PDF written  → {pdf_path} ({size_kb} KB)')
    print(sep)


if __name__ == '__main__':
    main()
