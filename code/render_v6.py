"""paper/anchor_word_v6.md -> HTML (inline print CSS) -> PDF via the browser's Page.printToPDF."""
import base64, os, sys, subprocess, markdown

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MD = os.path.join(ROOT, "paper", "anchor_word_v6.md")
HTML = os.path.join(ROOT, "paper", "paper.html")
PDF = os.path.join(ROOT, "paper", "anchor_word_v6.pdf")

CSS = """
@page { size: A4; margin: 17mm 15mm 16mm 15mm; }
body { font-family: Georgia, "DejaVu Serif", serif; font-size: 9.9pt; line-height: 1.48; color: #1a1a1a; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 2mm; }
h2 { font-size: 12.2pt; margin: 6mm 0 2mm; page-break-after: avoid; border-bottom: 0.6pt solid #c9ced6; padding-bottom: 1mm; }
h3 { font-size: 10.4pt; margin: 4.5mm 0 1.5mm; page-break-after: avoid; }
p { text-align: left; margin: 0 0 2.4mm; }   /* justified text rivers around long paths */
ul, ol { margin: 0 0 2.6mm 5mm; padding: 0; }
li { margin-bottom: 1mm; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.4pt; background: #f2f3f5; padding: 0 0.6mm; }
pre { white-space: pre-wrap; word-break: break-word; page-break-inside: avoid; background: #f7f8f9; padding: 2mm; }
table { border-collapse: collapse; width: 100%; font-size: 8.1pt; margin: 1.5mm 0 3mm; page-break-inside: avoid; }
th, td { border: 0.5pt solid #c9ced6; padding: 1.1mm 1.6mm; vertical-align: top; }
th { background: #eef0f3; font-weight: normal; text-align: left; }
blockquote { margin: 2mm 0 2mm 4mm; padding-left: 3mm; border-left: 2pt solid #c9ced6; color: #333; }
img { max-width: 100%; display: block; margin: 2mm auto 1mm; }
.caption { font-size: 8.2pt; color: #555; text-align: center; margin-bottom: 4mm; }
.tblock { page-break-inside: avoid; break-inside: avoid; }
"""


def build_html():
    md = open(MD).read()
    body = markdown.markdown(md, extensions=["tables", "fenced_code", "sane_lists"])
    # keep a table caption and its table on one page: markdown emits them as
    # <p><strong>Table N.</strong> ...</p> followed by <table>. Without this the caption
    # can strand at the foot of a page while the table moves to the next one.
    import re as _re
    body = _re.sub(r"(<p><strong>Table [0-9]+[ab]?\.</strong>.*?</p>)\s*(<table>)",
                   r'<div class="tblock">\1\2', body, flags=_re.S)
    body = body.replace("</table>", "</table></div>")
    body = body.replace('<div class="tblock"></div>', "")
    html = (f"<!doctype html><html><head><meta charset='utf-8'>"
            f"<title>Position Curse: surface-order decomposition</title>"
            f"<style>{CSS}</style></head><body>{body}</body></html>")
    open(HTML, "w").write(html)
    return html


def main():
    build_html()
    print("html bytes", os.path.getsize(HTML))
    print("now print with the browser helper (see main session)")


if __name__ == "__main__":
    main()
