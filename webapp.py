"""Web app keo-tha file: kiem tra chinh ta & dinh dang file Word tren trinh duyet.

Chay:
    python webapp.py
Sau do mo http://127.0.0.1:5000 va keo file .docx vao.

Luu y: chay cuc bo tren may ban (localhost), khong co xac thuc. Khong nen mo ra
internet cong cong vi bat ky ai cung co the upload file.
"""

import os
import tempfile

from flask import Flask, jsonify, render_template, request, send_file

import config
from checker.annotate import annotate
from checker.autofix import autofix
from checker.document import load_document
from checker.issues import SEVERITY_ERROR
from checker.learn_profile import learn_profile
from checker.resources import resource_path
from checker.runner import run_checks
from checker.stats import compute_stats

app = Flask(
    __name__,
    template_folder=resource_path("web"),
    static_folder=resource_path("web", "static"),
)

# Gioi han kich thuoc upload: 25 MB
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024
ALLOWED_EXT = ".docx"


def _issue_to_dict(it) -> dict:
    return {
        "category": it.category,
        "severity": it.severity,
        "message": it.message,
        "location": it.location(),
        "paragraph": it.paragraph,
        "excerpt": it.excerpt,
        "suggestion": it.suggestion,
    }


def _save_upload(file_storage) -> str:
    """Luu file upload ra file tam, tra ve duong dan."""
    fd, tmp_path = tempfile.mkstemp(suffix=".docx")
    os.close(fd)
    file_storage.save(tmp_path)
    return tmp_path


def _resolve_profile(req):
    """Lay profile: uu tien hoc tu file mau 'template' neu co, nguoc lai theo ten."""
    tpl = req.files.get("template")
    if tpl and tpl.filename and tpl.filename.lower().endswith(".docx"):
        tmp = _save_upload(tpl)
        try:
            return learn_profile(tmp)
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
    return config.get_profile(req.form.get("profile", config.DEFAULT_PROFILE))


def _valid_upload(req):
    if "file" not in req.files:
        return None, "Khong co file nao duoc gui len."
    f = req.files["file"]
    if not f.filename:
        return None, "Chua chon file."
    if not f.filename.lower().endswith(ALLOWED_EXT):
        return None, "Chi ho tro file .docx (Word)."
    return f, None


@app.route("/")
def index():
    return render_template(
        "index.html",
        profiles=list(config.PROFILES),
        default=config.DEFAULT_PROFILE,
        llm_enabled=config.llm_enabled(),
    )


@app.route("/favicon.ico")
def favicon():
    path = resource_path("assets", "icon.ico")
    if os.path.exists(path):
        return send_file(path, mimetype="image/x-icon")
    return ("", 404)


@app.route("/check", methods=["POST"])
def check():
    f, err = _valid_upload(request)
    if err:
        return jsonify({"error": err}), 400

    profile = _resolve_profile(request)
    do_format = request.form.get("format", "1") == "1"
    do_text = request.form.get("text", "1") == "1"
    do_spelling = request.form.get("spelling", "1") == "1"
    do_llm = request.form.get("llm", "0") == "1"
    if do_llm and not config.llm_enabled():
        return jsonify({"error": "Chua cau hinh LLM_API_KEY tren server."}), 400

    tmp_path = _save_upload(f)
    try:
        issues = run_checks(tmp_path, profile, do_format, do_text, do_spelling, do_llm,
                            do_headings=request.form.get("headings", "1") == "1")
        stats = compute_stats(load_document(tmp_path))
    except Exception as e:
        return jsonify({"error": f"Khong doc duoc file: {e}"}), 400
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass

    errors = sum(1 for it in issues if it.severity == SEVERITY_ERROR)
    by_cat = {}
    for it in issues:
        by_cat[it.category] = by_cat.get(it.category, 0) + 1

    return jsonify({
        "filename": f.filename,
        "summary": {"total": len(issues), "errors": errors, "by_category": by_cat},
        "stats": stats,
        "issues": [_issue_to_dict(it) for it in issues],
    })


@app.route("/fix", methods=["POST"])
def fix():
    f, err = _valid_upload(request)
    if err:
        return jsonify({"error": err}), 400

    do_spelling = request.form.get("spelling", "1") == "1"
    do_fix_format = request.form.get("fix_format", "0") == "1"
    profile = _resolve_profile(request) if do_fix_format else None

    tmp_in = _save_upload(f)
    fd, tmp_out = tempfile.mkstemp(suffix=".docx")
    os.close(fd)
    try:
        autofix(
            tmp_in, tmp_out,
            max_consecutive_empty=config.MAX_CONSECUTIVE_EMPTY,
            fix_spelling=do_spelling,
            fix_format=do_fix_format,
            profile=profile,
        )
    except Exception as e:
        return jsonify({"error": f"Khong sua duoc file: {e}"}), 400
    finally:
        try:
            os.remove(tmp_in)
        except OSError:
            pass

    base, ext = os.path.splitext(f.filename)
    download_name = f"{base}_fixed{ext}"
    return send_file(
        tmp_out,
        as_attachment=True,
        download_name=download_name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


@app.route("/annotate", methods=["POST"])
def annotate_route():
    f, err = _valid_upload(request)
    if err:
        return jsonify({"error": err}), 400

    profile = _resolve_profile(request)
    do_format = request.form.get("format", "1") == "1"
    do_text = request.form.get("text", "1") == "1"
    do_spelling = request.form.get("spelling", "1") == "1"

    tmp_in = _save_upload(f)
    fd, tmp_out = tempfile.mkstemp(suffix=".docx")
    os.close(fd)
    try:
        issues = run_checks(tmp_in, profile, do_format, do_text, do_spelling)
        annotate(tmp_in, tmp_out, issues)
    except Exception as e:
        return jsonify({"error": f"Khong tao duoc file chu thich: {e}"}), 400
    finally:
        try:
            os.remove(tmp_in)
        except OSError:
            pass

    base, ext = os.path.splitext(f.filename)
    download_name = f"{base}_commented{ext}"
    return send_file(
        tmp_out,
        as_attachment=True,
        download_name=download_name,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


if __name__ == "__main__":
    print("Mo trinh duyet tai: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
