"""Tao bao cao ket qua kiem tra: ra man hinh va xuat file HTML."""

import html
from collections import defaultdict

from .issues import (
    CATEGORY_FORMAT,
    CATEGORY_HEADING,
    CATEGORY_SPELLING,
    CATEGORY_SPELLING_AI,
    CATEGORY_TEXT,
    SEVERITY_ERROR,
    Issue,
)

_CATEGORY_ORDER = [CATEGORY_SPELLING, CATEGORY_SPELLING_AI, CATEGORY_HEADING, CATEGORY_FORMAT, CATEGORY_TEXT]


def _sort_key(issue: Issue):
    return (
        _CATEGORY_ORDER.index(issue.category) if issue.category in _CATEGORY_ORDER else 99,
        issue.paragraph if issue.paragraph is not None else -1,
    )


def summarize(issues: list[Issue]) -> dict:
    by_cat = defaultdict(int)
    errors = 0
    for it in issues:
        by_cat[it.category] += 1
        if it.severity == SEVERITY_ERROR:
            errors += 1
    return {"total": len(issues), "errors": errors, "by_category": dict(by_cat)}


def print_report(path: str, issues: list[Issue]) -> None:
    print("=" * 64)
    print(f"  BAO CAO KIEM TRA: {path}")
    print("=" * 64)

    if not issues:
        print("\n  Khong phat hien loi nao. File san sang de nop!\n")
        return

    s = summarize(issues)
    print(f"\n  Tong cong: {s['total']} van de  (loi nghiem trong: {s['errors']})")
    for cat, cnt in s["by_category"].items():
        print(f"    - {cat}: {cnt}")
    print()

    for it in sorted(issues, key=_sort_key):
        mark = "[X]" if it.severity == SEVERITY_ERROR else "[!]"
        print(f"  {mark} [{it.category}] {it.location()}: {it.message}")
        if it.excerpt:
            print(f"        > {it.excerpt}")
        if it.suggestion:
            print(f"        -> {it.suggestion}")
    print()


def write_html(path: str, src_path: str, issues: list[Issue]) -> None:
    s = summarize(issues)
    rows = []
    for it in sorted(issues, key=_sort_key):
        sev_cls = "err" if it.severity == SEVERITY_ERROR else "warn"
        rows.append(
            f"<tr class='{sev_cls}'>"
            f"<td>{html.escape(it.category)}</td>"
            f"<td>{html.escape(it.location())}</td>"
            f"<td>{html.escape(it.message)}</td>"
            f"<td class='ex'>{html.escape(it.excerpt)}</td>"
            f"<td>{html.escape(it.suggestion)}</td>"
            f"</tr>"
        )
    rows_html = "\n".join(rows) if rows else "<tr><td colspan='5'>Khong co loi nao.</td></tr>"

    cats = "".join(
        f"<li>{html.escape(c)}: <b>{n}</b></li>" for c, n in s["by_category"].items()
    )

    doc = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Bao cao kiem tra Word</title>
<style>
  body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #222; }}
  h1 {{ font-size: 20px; }}
  .meta {{ color: #555; margin-bottom: 16px; }}
  .summary {{ background:#f4f6f8; border:1px solid #e0e4e8; border-radius:8px; padding:12px 16px; margin-bottom:20px; }}
  .summary ul {{ margin:6px 0 0; padding-left:18px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ border: 1px solid #e0e4e8; padding: 8px 10px; text-align: left; vertical-align: top; }}
  th {{ background: #2b6cb0; color: #fff; }}
  tr.err td {{ background: #fff5f5; }}
  tr.warn td {{ background: #fffaf0; }}
  td.ex {{ color:#444; font-family: Consolas, monospace; font-size:13px; }}
  .ok {{ color: #2f855a; font-weight: bold; font-size: 16px; }}
</style>
</head>
<body>
  <h1>Bao cao kiem tra chinh ta &amp; dinh dang</h1>
  <div class="meta">File: {html.escape(src_path)}</div>
  <div class="summary">
    Tong cong: <b>{s['total']}</b> van de &middot; loi nghiem trong: <b>{s['errors']}</b>
    <ul>{cats}</ul>
  </div>
  {"<p class='ok'>File san sang de nop!</p>" if not issues else ""}
  <table>
    <thead><tr><th>Nhom</th><th>Vi tri</th><th>Mo ta</th><th>Trich doan</th><th>Goi y</th></tr></thead>
    <tbody>
    {rows_html}
    </tbody>
  </table>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(doc)


def _issue_rows(issues: list[Issue]) -> str:
    rows = []
    for it in sorted(issues, key=_sort_key):
        sev_cls = "err" if it.severity == SEVERITY_ERROR else "warn"
        rows.append(
            f"<tr class='{sev_cls}'>"
            f"<td>{html.escape(it.category)}</td>"
            f"<td>{html.escape(it.location())}</td>"
            f"<td>{html.escape(it.message)}</td>"
            f"<td class='ex'>{html.escape(it.excerpt)}</td>"
            f"<td>{html.escape(it.suggestion)}</td>"
            f"</tr>"
        )
    return "\n".join(rows) if rows else "<tr><td colspan='5'>Khong co loi nao.</td></tr>"


_HTML_STYLE = """
  body { font-family: Segoe UI, Arial, sans-serif; margin: 24px; color: #222; }
  h1 { font-size: 20px; }
  h2 { font-size: 16px; margin-top: 28px; border-bottom: 2px solid #2b6cb0; padding-bottom: 4px; }
  .meta { color: #555; margin-bottom: 16px; }
  .summary { background:#f4f6f8; border:1px solid #e0e4e8; border-radius:8px; padding:12px 16px; margin-bottom:20px; }
  .summary ul { margin:6px 0 0; padding-left:18px; }
  table { border-collapse: collapse; width: 100%; font-size: 14px; margin-bottom:8px; }
  th, td { border: 1px solid #e0e4e8; padding: 8px 10px; text-align: left; vertical-align: top; }
  th { background: #2b6cb0; color: #fff; }
  tr.err td { background: #fff5f5; }
  tr.warn td { background: #fffaf0; }
  td.ex { color:#444; font-family: Consolas, monospace; font-size:13px; }
  .ok { color: #2f855a; font-weight: bold; }
"""


def write_html_multi(out_path: str, results: list[tuple[str, list[Issue]]]) -> None:
    """Xuat bao cao gop cho nhieu file (che do kiem thu muc)."""
    total = sum(len(iss) for _, iss in results)
    total_err = sum(
        1 for _, iss in results for it in iss if it.severity == SEVERITY_ERROR
    )

    sections = []
    for src, issues in results:
        s = summarize(issues)
        head = (
            f"<h2>{html.escape(src)}</h2>"
            f"<div class='summary'>Tong: <b>{s['total']}</b> &middot; "
            f"loi nghiem trong: <b>{s['errors']}</b></div>"
        )
        if not issues:
            sections.append(head + "<p class='ok'>File san sang de nop!</p>")
            continue
        table = (
            "<table><thead><tr><th>Nhom</th><th>Vi tri</th><th>Mo ta</th>"
            "<th>Trich doan</th><th>Goi y</th></tr></thead><tbody>"
            + _issue_rows(issues)
            + "</tbody></table>"
        )
        sections.append(head + table)

    doc = f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Bao cao kiem tra Word (nhieu file)</title>
<style>{_HTML_STYLE}</style>
</head>
<body>
  <h1>Bao cao kiem tra chinh ta &amp; dinh dang</h1>
  <div class="summary">
    So file: <b>{len(results)}</b> &middot; tong van de: <b>{total}</b> &middot;
    loi nghiem trong: <b>{total_err}</b>
  </div>
  {''.join(sections)}
</body>
</html>"""
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
