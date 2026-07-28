"""
Inject the frozen results bundle into the page template to produce index.html.

The data is inlined rather than fetched because a page opened from the file
system cannot fetch a sibling JSON file: the browser blocks it as a
cross-origin request. Inlining is what makes the double-click path work with no
server, which is the whole point of shipping a single file.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent
TEMPLATE = ROOT / "page_template.html"
BUNDLE = ROOT / "bundle.json"
OUT = ROOT / "index.html"
MARKER = "/*__FROZEN_DATA__*/null"


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    html = TEMPLATE.read_text(encoding="utf-8")
    if MARKER not in html:
        raise SystemExit(f"marker {MARKER!r} not found in {TEMPLATE.name}")

    data = json.loads(BUNDLE.read_text(encoding="utf-8"))
    # </script> inside any string would close the script block early.
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")

    OUT.write_text(html.replace(MARKER, payload), encoding="utf-8")

    size = OUT.stat().st_size / 1024
    print(f"{OUT.name} written, {size:.0f} KB")
    print(f"  {len(data['questions'])} questions bundled")

    # Guards that would otherwise fail silently in the browser.
    text = OUT.read_text(encoding="utf-8")
    problems = []
    if "AIza" in text:
        problems.append("an API key appears to be embedded")
    if size > 400:
        problems.append(f"page is {size:.0f} KB, over the 400 KB budget")
    if MARKER in text:
        problems.append("placeholder was not replaced")
    print("  checks:", "; ".join(problems) if problems else "no key, size OK, data injected")


if __name__ == "__main__":
    main()
