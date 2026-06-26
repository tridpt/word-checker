"""Tool kiem tra chinh ta & dinh dang file Word truoc khi nop.

Cach dung:
    python cli.py bai_tap.docx
    python cli.py bai_tap.docx --html bao_cao.html
    python cli.py bai_tap.docx --profile luan_van
    python cli.py bai_tap.docx --fix              # tu dong sua, luu ra *_fixed.docx
    python cli.py thu_muc_bai_tap                 # kiem ca thu muc
    python cli.py bai_tap.docx --no-spelling
"""

import argparse
import json
import os
import sys

# Dam bao in tieng Viet ra console khong bi loi tren Windows (code page cp1252).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import config
from checker.annotate import annotate
from checker.autofix import autofix
from checker.document import load_document
from checker.issues import SEVERITY_ERROR
from checker.learn_profile import describe_profile, learn_profile
from checker.report import print_report, write_html, write_html_multi
from checker.runner import run_checks
from checker.stats import compute_stats


def _gather_docx(path: str) -> list[str]:
    """Tra ve danh sach file .docx tu mot file hoac thu muc."""
    if os.path.isdir(path):
        files = []
        for name in sorted(os.listdir(path)):
            if name.lower().endswith(".docx") and not name.startswith("~$"):
                files.append(os.path.join(path, name))
        return files
    return [path]


def _check_one(path: str, profile: dict, args) -> list:
    return run_checks(
        path, profile,
        do_format=not args.no_format,
        do_text=not args.no_text,
        do_spelling=not args.no_spelling,
        do_llm_spelling=args.llm_spelling,
        do_headings=not args.no_headings,
        limits=_limits_from_args(args),
        skip_math=not args.no_skip_math,
    )


def _limits_from_args(args) -> dict:
    """Lay gioi han tu CLI; thieu thi dung gia tri trong config."""
    return {
        "min_words": args.min_words if args.min_words is not None else config.LIMITS.get("min_words"),
        "max_words": args.max_words if args.max_words is not None else config.LIMITS.get("max_words"),
        "max_pages": args.max_pages if args.max_pages is not None else config.LIMITS.get("max_pages"),
    }


def _suffix_path(src: str, suffix: str) -> str:
    base, ext = os.path.splitext(src)
    return base + suffix + ext


def run(args) -> int:
    path = args.file
    if not os.path.exists(path):
        print(f"Loi: khong tim thay '{path}'", file=sys.stderr)
        return 2

    profile = config.get_profile(args.profile)

    # Hoc quy chuan tu file mau neu co --template (uu tien hon --profile)
    if args.template:
        if not os.path.exists(args.template) or not args.template.lower().endswith(".docx"):
            print(f"Loi: file mau '{args.template}' khong ton tai hoac khong phai .docx", file=sys.stderr)
            return 2
        try:
            profile = learn_profile(args.template)
        except Exception as e:
            print(f"Loi khi hoc quy chuan tu file mau: {e}", file=sys.stderr)
            return 2
        print(f"  Da hoc quy chuan tu file mau: {args.template}")
        print(describe_profile(profile))
        print()

    if args.llm_spelling and not config.llm_enabled():
        print("Loi: --llm-spelling can cau hinh LLM_API_KEY (xem .env.example).", file=sys.stderr)
        return 2

    files = _gather_docx(path)
    if not files:
        print(f"Khong tim thay file .docx nao trong '{path}'", file=sys.stderr)
        return 2

    # Loc bo file khong phai .docx (truong hop chi dinh file le)
    valid = [f for f in files if f.lower().endswith(".docx")]
    if not valid:
        print("Loi: chi ho tro file .docx. File .doc cu can luu lai thanh .docx.", file=sys.stderr)
        return 2

    # Che do tu dong sua (chi ap dung khi chi dinh 1 file de an toan/de hieu)
    if args.fix or args.fix_format:
        if len(valid) != 1:
            print("Luu y: --fix chi ap dung cho mot file. Hay chi dinh dung mot file .docx.", file=sys.stderr)
            return 2
        out = args.out or _suffix_path(valid[0], "_fixed")
        stats = autofix(
            valid[0], out,
            max_consecutive_empty=config.MAX_CONSECUTIVE_EMPTY,
            fix_spelling=not args.no_spelling,
            fix_format=args.fix_format,
            profile=profile,
        )
        msg = (f"  Da sua {stats['text_and_spelling_fixes']} loi van ban/chinh ta, "
               f"xoa {stats['empty_paragraphs_removed']} doan trong thua")
        if args.fix_format:
            msg += f", chinh {stats['format_fixes']} cho dinh dang"
        print(msg + ".")
        print(f"  Da luu file da sua: {out}\n")
        print("  Kiem tra lai file da sua:")
        # kiem lai file da sua de bao cao phan con sot
        valid = [out]

    results = []
    stats_by_file = {}
    for f in valid:
        try:
            issues = _check_one(f, profile, args)
            stats_by_file[f] = compute_stats(load_document(f))
        except Exception as e:
            print(f"Loi khi doc '{f}': {e}", file=sys.stderr)
            continue
        results.append((f, issues))

    # In ket qua
    if len(results) == 1:
        print_report(results[0][0], results[0][1], stats_by_file.get(results[0][0]))
    else:
        for f, issues in results:
            print_report(f, issues, stats_by_file.get(f))
        total = sum(len(iss) for _, iss in results)
        print("=" * 64)
        print(f"  TONG KET: {len(results)} file, {total} van de.")
        print("=" * 64 + "\n")

    # Xuat HTML
    if args.html:
        if len(results) == 1:
            write_html(args.html, results[0][0], results[0][1])
        else:
            write_html_multi(args.html, results)
        print(f"  Da xuat bao cao HTML: {args.html}\n")

    # Xuat PDF (chi file dau tien neu kiem nhieu file)
    if args.pdf:
        from checker.pdf_report import write_pdf
        f0, iss0 = results[0]
        try:
            write_pdf(args.pdf, f0, iss0, stats_by_file.get(f0))
            print(f"  Da xuat bao cao PDF: {args.pdf}\n")
        except Exception as e:
            print(f"  Khong tao duoc PDF: {e}", file=sys.stderr)

    # Xuat JSON
    if args.json:
        payload = [
            {
                "file": f,
                "issues": [it.to_dict() for it in iss],
            }
            for f, iss in results
        ]
        with open(args.json, "w", encoding="utf-8") as jf:
            json.dump(payload, jf, ensure_ascii=False, indent=2)
        print(f"  Da xuat ket qua JSON: {args.json}\n")

    # Xuat file Word co comment tai cho loi
    if args.annotate:
        for f, iss in results:
            out = _suffix_path(f, "_commented")
            try:
                stats = annotate(f, out, iss)
                print(f"  Da tao file co chu thich: {out} ({stats['comments_added']} comment)")
            except Exception as e:
                print(f"  Khong tao duoc file chu thich cho '{f}': {e}", file=sys.stderr)
        print()

    has_error = any(
        it.severity == SEVERITY_ERROR for _, iss in results for it in iss
    )
    return 1 if has_error else 0


def main():
    parser = argparse.ArgumentParser(
        description="Kiem tra chinh ta & dinh dang file Word (.docx) truoc khi nop."
    )
    parser.add_argument("file", help="Duong dan toi file .docx hoac thu muc chua cac file .docx")
    parser.add_argument("--profile", help=f"Profile quy chuan: {', '.join(config.PROFILES)} (mac dinh: {config.DEFAULT_PROFILE})")
    parser.add_argument("--template", metavar="REF.docx", help="Hoc quy chuan tu file .docx mau (uu tien hon --profile)")
    parser.add_argument("--fix", action="store_true", help="Tu dong sua loi co hoc/chinh ta, luu ra file moi")
    parser.add_argument("--fix-format", action="store_true", help="Tu dong sua ca dinh dang theo profile (font, co chu, gian dong, canh le)")
    parser.add_argument("--max-words", type=int, help="Canh bao neu vuot so tu nay")
    parser.add_argument("--min-words", type=int, help="Canh bao neu thieu so tu nay")
    parser.add_argument("--max-pages", type=int, help="Canh bao neu vuot so trang (uoc tinh) nay")
    parser.add_argument("--out", metavar="FILE", help="Ten file ket qua khi dung --fix (mac dinh: *_fixed.docx)")
    parser.add_argument("--html", metavar="OUT", help="Xuat bao cao ra file HTML")
    parser.add_argument("--pdf", metavar="OUT", help="Xuat bao cao ra file PDF")
    parser.add_argument("--json", metavar="OUT", help="Xuat ket qua ra file JSON (cho tu dong hoa)")
    parser.add_argument("--annotate", action="store_true", help="Xuat ban sao .docx co comment tai cho loi (*_commented.docx)")
    parser.add_argument("--no-format", action="store_true", help="Bo qua kiem tra dinh dang")
    parser.add_argument("--no-text", action="store_true", help="Bo qua kiem tra loi co hoc van ban")
    parser.add_argument("--no-headings", action="store_true", help="Bo qua kiem tra tieu de muc & danh so")
    parser.add_argument("--no-skip-math", action="store_true", help="Khong bo qua doan cong thuc (kiem tra ca vung toan hoc)")
    parser.add_argument("--no-spelling", action="store_true", help="Bo qua kiem tra chinh ta")
    parser.add_argument("--llm-spelling", action="store_true", help="Bat kiem tra chinh ta bang AI/LLM (can cau hinh LLM_API_KEY)")
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
