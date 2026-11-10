"""
Builds Publication-Grade Printable HTML and PDF documents for Project Report and Phase 1 Design.
"""

from pathlib import Path
import re
import html

CSS_STYLES = """
<style>
    @page {
        size: A4;
        margin: 20mm;
    }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
        line-height: 1.6;
        color: #1e293b;
        background-color: #ffffff;
        max-width: 950px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    h1 {
        color: #0f172a;
        font-size: 2.2rem;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 10px;
        margin-top: 30px;
        font-weight: 800;
    }
    h2 {
        color: #1e3a8a;
        font-size: 1.6rem;
        border-bottom: 1.5px solid #cbd5e1;
        padding-bottom: 6px;
        margin-top: 35px;
        page-break-after: avoid;
    }
    h3 {
        color: #1e40af;
        font-size: 1.25rem;
        margin-top: 25px;
        page-break-after: avoid;
    }
    h4 {
        color: #334155;
        font-size: 1.05rem;
        margin-top: 15px;
    }
    p, li {
        font-size: 1.0rem;
        color: #334155;
    }
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 0.92rem;
        page-break-inside: avoid;
    }
    th, td {
        border: 1px solid #cbd5e1;
        padding: 10px 12px;
        text-align: left;
    }
    th {
        background-color: #f1f5f9;
        color: #0f172a;
        font-weight: 700;
    }
    tr:nth-child(even) {
        background-color: #f8fafc;
    }
    pre {
        background-color: #0f172a;
        color: #f8fafc;
        padding: 14px 18px;
        border-radius: 6px;
        overflow-x: auto;
        font-family: Consolas, "Courier New", monospace;
        font-size: 0.88rem;
        line-height: 1.45;
        page-break-inside: avoid;
    }
    code {
        font-family: Consolas, "Courier New", monospace;
        background-color: #f1f5f9;
        color: #0284c7;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.9em;
    }
    pre code {
        background-color: transparent;
        color: inherit;
        padding: 0;
    }
    blockquote {
        border-left: 4px solid #3b82f6;
        padding-left: 16px;
        margin: 16px 0;
        color: #475569;
        background-color: #eff6ff;
        padding: 10px 16px;
        border-radius: 0 4px 4px 0;
    }
    hr {
        border: 0;
        height: 1px;
        background: #e2e8f0;
        margin: 30px 0;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 4px;
        background-color: #dbeafe;
        color: #1e40af;
    }
    @media print {
        body {
            padding: 0;
            max-width: 100%;
        }
        .page-break {
            page-break-before: always;
        }
    }
</style>
"""

def markdown_to_html(md_text: str, title: str) -> str:
    """Robust Markdown to HTML parser for project reports."""
    lines = md_text.splitlines()
    html_lines = []
    
    in_code_block = False
    in_table = False
    table_header_done = False
    
    for line in lines:
        stripped = line.strip()
        
        # Code blocks
        if stripped.startswith("```"):
            if in_code_block:
                html_lines.append("</code></pre>")
                in_code_block = False
            else:
                html_lines.append("<pre><code>")
                in_code_block = True
            continue
            
        if in_code_block:
            html_lines.append(html.escape(line))
            continue
            
        # Tables
        if "|" in line and (line.startswith("|") or line.endswith("|")):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            # Check if separator row
            if all(re.match(r"^:?-+:?$", c) for c in cells):
                table_header_done = True
                continue
                
            if not in_table:
                html_lines.append("<table>")
                in_table = True
                table_header_done = False
                
            tag = "th" if not table_header_done else "td"
            row_html = "<tr>" + "".join(f"<{tag}>{format_inline(c)}</{tag}>" for c in cells) + "</tr>"
            html_lines.append(row_html)
            continue
        else:
            if in_table:
                html_lines.append("</table>")
                in_table = False
                
        # Empty line
        if not stripped:
            html_lines.append("<br/>")
            continue
            
        # Headers
        if stripped.startswith("# "):
            html_lines.append(f"<h1>{format_inline(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{format_inline(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{format_inline(stripped[4:])}</h3>")
        elif stripped.startswith("#### "):
            html_lines.append(f"<h4>{format_inline(stripped[5:])}</h4>")
        elif stripped.startswith("---"):
            html_lines.append("<hr/>")
        elif stripped.startswith("- ") or stripped.startswith("* "):
            html_lines.append(f"<ul><li>{format_inline(stripped[2:])}</li></ul>")
        elif re.match(r"^\d+\.\s+", stripped):
            match = re.match(r"^\d+\.\s+(.*)", stripped)
            html_lines.append(f"<ol><li>{format_inline(match.group(1))}</li></ol>")
        else:
            html_lines.append(f"<p>{format_inline(line)}</p>")
            
    if in_table:
        html_lines.append("</table>")
    if in_code_block:
        html_lines.append("</code></pre>")
        
    body_content = "\n".join(html_lines)
    
    # Consolidate consecutive <ul> and <ol>
    body_content = re.sub(r"</ul>\s*<ul>", "", body_content)
    body_content = re.sub(r"</ol>\s*<ol>", "", body_content)
    
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    {CSS_STYLES}
</head>
<body>
    {body_content}
</body>
</html>
"""
    return full_html


def format_inline(text: str) -> str:
    """Formats bold, italic, code, and links in markdown text."""
    # Escape HTML first
    escaped = html.escape(text)
    # Bold **text**
    escaped = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", escaped)
    # Inline code `code`
    escaped = re.sub(r"`(.*?)`", r"<code>\1</code>", escaped)
    # LaTeX math approximation: $...$ -> <em>...</em>
    escaped = re.sub(r"\$(.*?)\$", r"<em>\1</em>", escaped)
    return escaped


def main():
    report_md = Path("documentation/project_report.md")
    if report_md.exists():
        content = report_md.read_text(encoding="utf-8")
        out_html = markdown_to_html(content, "OS Simulator — Comprehensive Project Report")
        Path("documentation/project_report.html").write_text(out_html, encoding="utf-8")
        print("Generated documentation/project_report.html")

    phase1_md = Path("Phase_1_Design/phase1_design.md")
    if phase1_md.exists():
        content = phase1_md.read_text(encoding="utf-8")
        out_html = markdown_to_html(content, "OS Simulator — Phase 1 Design Master")
        Path("Phase_1_Design/phase1_design.html").write_text(out_html, encoding="utf-8")
        print("Generated Phase_1_Design/phase1_design.html")

if __name__ == "__main__":
    main()
