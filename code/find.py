"""Page-level search over a PDF, so citations can name a page.

Usage: python3 find.py <pdf> <term> [term...]
"""
import re
import subprocess
import sys


def page_text(pdf, page):
    out = subprocess.run(["pdftotext", "-layout", "-f", str(page), "-l", str(page), pdf, "-"],
                         capture_output=True, text=True)
    return out.stdout


def main():
    pdf = sys.argv[1]
    terms = [t.lower() for t in sys.argv[2:]]
    pages = int(re.search(r"Pages:\s+(\d+)",
                          subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout).group(1))
    for p in range(1, pages + 1):
        txt = page_text(pdf, p)
        low = txt.lower()
        hits = [t for t in terms if t in low]
        if not hits:
            continue
        for t in hits:
            for m in re.finditer(re.escape(t), low):
                s = max(0, m.start() - 110)
                snippet = " ".join(txt[s:m.start() + 150].split())
                print(f"p{p} [{t}] ...{snippet}...")
        print()


if __name__ == "__main__":
    main()
