"""
routes/dashboard.py — Main dashboard overview and global search.
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models import db, VaultFile, Note, Link, PasswordEntry
from utils.crypto import decrypt

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    uid = current_user.id
    stats = {
        "files":     VaultFile.query.filter_by(user_id=uid).count(),
        "notes":     Note.query.filter_by(user_id=uid).count(),
        "links":     Link.query.filter_by(user_id=uid).count(),
        "passwords": PasswordEntry.query.filter_by(user_id=uid).count(),
    }
    recent_files = (VaultFile.query.filter_by(user_id=uid)
                    .order_by(VaultFile.uploaded_at.desc()).limit(5).all())
    recent_notes = (Note.query.filter_by(user_id=uid)
                    .order_by(Note.updated_at.desc()).limit(5).all())
    return render_template("dashboard/index.html",
                           stats=stats,
                           recent_files=recent_files,
                           recent_notes=recent_notes)


@dashboard_bp.route("/search")
@login_required
def search():
    """Global search across notes, links, and password entries."""
    q   = request.args.get("q", "").strip().lower()
    uid = current_user.id

    results = {"notes": [], "links": [], "passwords": [], "files": []}

    if q:
        # Files
        for f in VaultFile.query.filter_by(user_id=uid).all():
            if q in f.original_name.lower():
                results["files"].append({
                    "id": f.id, "name": f.original_name,
                    "type": f.file_type, "size": f.size_human
                })

        # Notes (search title + decrypted content)
        for n in Note.query.filter_by(user_id=uid).all():
            if q in n.title.lower() or q in decrypt(n.content).lower() or q in n.tags.lower():
                results["notes"].append({"id": n.id, "title": n.title, "tags": n.tags})

        # Links
        for lk in Link.query.filter_by(user_id=uid).all():
            if q in lk.title.lower() or q in lk.url.lower() or q in lk.tags.lower():
                results["links"].append({"id": lk.id, "title": lk.title, "url": lk.url})

        # Passwords — search site name and username only (never decrypt for search)
        for p in PasswordEntry.query.filter_by(user_id=uid).all():
            if q in p.site_name.lower() or q in p.username.lower():
                results["passwords"].append({"id": p.id, "site": p.site_name, "user": p.username})

    return jsonify(results)
