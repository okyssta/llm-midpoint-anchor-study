"""paper/novelty_audit.md -> HTML -> PDF, reusing the paper's print CSS."""
import os

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MD = os.path.join(ROOT, "paper", "novelty_audit.md")
HTML = os.path.join(ROOT, "paper", "novelty_audit.html")

CSS = """
@page { size: A4; margin: 15mm 13mm 14mm 13mm; }
body { font-family: Georgia, "DejaVu Serif", serif; font-size: 9.1pt; line-height: 1.41; color: #1a1a1a;
       orphans: 3; widows: 3; }
h1 { font-size: 16pt; line-height: 1.22; margin: 0 0 2mm; }
h2 { font-size: 11.4pt; margin: 4.4mm 0 1.8mm; page-break-after: avoid; border-bottom: 0.6pt solid #c9ced6; padding-bottom: 1mm; }
h3 { font-size: 10pt; margin: 4mm 0 1.5mm; page-break-after: avoid; }
p { margin: 0 0 2.2mm; }
ul, ol { margin: 0 0 2.4mm 5mm; padding: 0; }
li { margin-bottom: 1.1mm; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8pt; background: #f2f3f5; padding: 0 0.6mm; }
table { border-collapse: collapse; width: 100%; font-size: 7.2pt; margin: 1.2mm 0 2.2mm; }
th, td { border: 0.5pt solid #c9ced6; padding: 1.1mm 1.4mm; vertical-align: top; }
th { background: #eef0f3; font-weight: normal; text-align: left; }
blockquote { margin: 2mm 0 2mm 3mm; padding-left: 3mm; border-left: 2pt solid #c9ced6; color: #333; }
"""


def main():
    body = markdown.markdown(open(MD).read(), extensions=["tables", "fenced_code", "sane_lists"])
    html = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>Novelty audit: anchor direction in list indexing</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    open(HTML, "w").write(html)
    print("wrote", HTML, len(html), "chars")


if __name__ == "__main__":
    main()
