"""
routes/files.py — File upload, listing, preview, download, and deletion.
Files are stored in UPLOAD_FOLDER with UUID-based names; originals never hit disk directly.
"""

import os
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, send_from_directory, abort, current_app, jsonify)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, VaultFile
from utils.security import allowed_file, safe_filename, get_mime_type, MAX_FILE_SIZE

files_bp = Blueprint("files", __name__, url_prefix="/files")


@files_bp.route("/")
@login_required
def index():
    tag    = request.args.get("tag", "")
    ftype  = request.args.get("type", "")
    query  = VaultFile.query.filter_by(user_id=current_user.id)

    if ftype == "image":
        query = query.filter(VaultFile.file_type.like("image/%"))
    elif ftype == "video":
        query = query.filter(VaultFile.file_type.like("video/%"))
    elif ftype == "doc":
        query = query.filter(VaultFile.file_type.like("application/%"))
    elif ftype == "text":
        query = query.filter(VaultFile.file_type.like("text/%"))

    all_files = query.order_by(VaultFile.uploaded_at.desc()).all()
    return render_template("dashboard/files.html", files=all_files, active_type=ftype)


@files_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    uploaded = request.files.getlist("files")
    if not uploaded:
        flash("No files selected.", "warning")
        return redirect(url_for("files.index"))

    success, skipped = 0, 0
    for file in uploaded:
        if not file or file.filename == "":
            continue

        original = secure_filename(file.filename)
        if not allowed_file(original):
            flash(f"'{original}' — file type not allowed.", "warning")
            skipped += 1
            continue

        # Read into memory to check size before writing
        data = file.read()
        if len(data) > MAX_FILE_SIZE:
            flash(f"'{original}' exceeds 50 MB limit.", "warning")
            skipped += 1
            continue

        stored_name = safe_filename(original)
        dest = os.path.join(current_app.config["UPLOAD_FOLDER"], stored_name)

        with open(dest, "wb") as fp:
            fp.write(data)

        mime = get_mime_type(dest)

        entry = VaultFile(
            user_id=current_user.id,
            filename=stored_name,
            original_name=original,
            file_type=mime,
            file_size=len(data),
        )
        db.session.add(entry)
        success += 1

    db.session.commit()
    if success:
        flash(f"{success} file(s) uploaded successfully.", "success")
    return redirect(url_for("files.index"))


@files_bp.route("/download/<int:file_id>")
@login_required
def download(file_id):
    f = VaultFile.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        f.filename,
        as_attachment=True,
        download_name=f.original_name
    )


@files_bp.route("/preview/<int:file_id>")
@login_required
def preview(file_id):
    """Serve file inline (for image/video preview in browser)."""
    f = VaultFile.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        f.filename,
        as_attachment=False
    )


@files_bp.route("/delete/<int:file_id>", methods=["POST"])
@login_required
def delete(file_id):
    f = VaultFile.query.filter_by(id=file_id, user_id=current_user.id).first_or_404()
    # Remove from disk
    path = os.path.join(current_app.config["UPLOAD_FOLDER"], f.filename)
    if os.path.exists(path):
        os.remove(path)
    db.session.delete(f)
    db.session.commit()
    flash("File deleted.", "success")
    return redirect(url_for("files.index"))


# ── API Endpoints ──────────────────────────────────────────────────────────

@files_bp.route("/api/list")
@login_required
def api_list():
    files = VaultFile.query.filter_by(user_id=current_user.id).order_by(VaultFile.uploaded_at.desc()).all()
    return jsonify([{
        "id": f.id,
        "name": f.original_name,
        "type": f.file_type,
        "size": f.file_size,
        "uploaded_at": f.uploaded_at.isoformat()
    } for f in files])
